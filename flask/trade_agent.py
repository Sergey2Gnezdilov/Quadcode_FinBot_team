from openai import OpenAI
from configparser import ConfigParser
import json
import os
import yfinance as yf
import numpy as np

class GPTAssistant:
    """
    A class to interact with OpenAI's GPT APIs.

    Attributes:
        client (OpenAI): The OpenAI client.
        default_model (str): The default model.
        assistant_prompt (dict): The assistant prompt.
        messages (list): The messages.
    """

    def __init__(self, model="gpt-4o"):
        api_key = ""
        self.client = OpenAI(api_key=api_key)
        self.default_model = model
        self.initialize_conversation()

    def constract_prompt(self):
        """
        Construct the assistant prompt.

        Parameters:
            db_name (str): The database name.
            db_schema (str): The database schema.
        """
        self.assistant_prompt = {
            "role": "system",
            "content": """
            You are a virtual assistant, you have a conversation with a user in natural language in order to help with Trading. The user is beginner to trading.
            
            The conversation for each query should consist of these steps:
            1) Ask the user of what is their experience with trading, the risk they are willing to take today, and how much money they are willing to invest.
            2) The user will provide the information.
            3) Based on the information provided by the user, you will personalise your future responses to the user.
            4) The user makes a query to buy or sell a stock.
            5) You retrieve the price and volatility of the stock from an API and ask the user to confirm the transaction, adapting your response to their risk level, making sure to inform them if a volatility is not suitable for their risk level.
            6) The user confirms the transaction.
            7) You make the transaction and provide the user with the transaction details.
            
            Ensure that the generated responses are suitable for a voice chat bot.
            Perform only one step at a time and never skip a step. Don't include the step number in your answers. Your answers should be concise.
            """ + "To get financial data return this API: getdata.com/ with payload /{stock/: , date/: /}" + "To make a transaction return this API: transaction.com/ with payload /{stock/: , price/: /}"
        }

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_stock_info",
                    "description": "Get the current stock price and volatility given the date",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stock_name": {
                                "type": "string",
                                "description": "The name code of the stock",
                            },
                            "date": {"type": "string", "description": "The date", "default": "today"},
                        },
                        "required": ["stock_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "trade_stock",
                    "description": "Buy or sell a stock at a given price",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stock_name": {
                                "type": "string",
                                "description": "The name code of the stock",
                            },
                            "price": {"type": "number", "description": "The price of the stock"},
                            "action": {"type": "string", "description": "The action to take", "enum": ["buy", "sell"]},
                        },
                        "required": ["stock_name", "price", "action"],
                    },
                },
            }
        ]

        return self.assistant_prompt

    def initialize_conversation(self):
        """
        Initialize the conversation.

        Parameters:
            db_name (str): The database name.
            db_schema (str): The database schema.
        """
        self.messages = [self.constract_prompt()]

    def conversation(self, user_input, model="default", max_tokens=150, temperature=0.2):
        """
        Generate a response to the user input.

        Parameters:
            user_input (str): The user input.
            model (str): The model to use.
            max_tokens (int): The maximum number of tokens to generate.
            temperature (float): The temperature.

        Returns:
            response (str): The response.
        """
        # if user has not specified a model, use the default model
        model = self.default_model if model == "default" else model

        # Add the user input to the history of messages
        self.messages.append({"role": "user", "content": user_input})

        # Generate Response
        self.client.completions
        completion = self.client.chat.completions.create(
            model=model,
            messages=self.messages,
            max_tokens=max_tokens,
            tools=self.tools,
            temperature=temperature,
        )

        # Handle the case where the model returns an empty response
        if not completion.choices:
            return "Sorry, I don't understand. Please rephrase your question."
        response = completion.choices[0].message.content
        tool_calls = completion.choices[0].message.tool_calls

        if tool_calls:
            available_functions = {
                "get_stock_info": self.get_stock_info,
                "trade_stock": self.trade_stock,
            }
            self.messages.append(completion.choices[0].message)
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = None
                if function_name == "get_stock_info":
                    function_response = function_to_call(
                        stock_name=function_args.get("stock_name"),
                        date=function_args.get("date"),
                    )
                elif function_name == "trade_stock":
                    function_response = function_to_call(
                        action=function_args.get("action"),
                        stock_name=function_args.get("stock_name"),
                        price=function_args.get("price"),
                    )

                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )

            response = self.client.chat.completions.create(
                model=model,
                messages=self.messages,
                max_tokens=max_tokens,
                temperature=temperature,
            ).choices[0].message.content

        # Remove any space or newline characters
        if response:
            response = response.strip()
        else:
            response = "Sorry, no response generated."

        # Add the response to the history of messages
        self.messages.append({"role": "system", "content": response})

        return response

    # Example dummy function hard coded to return the price
    # of a specific stock on a specific date
    def get_stock_info(self, stock_name, date):
        try:
            """Get the current stock price and volatility in a given date"""
            stock = yf.Ticker(stock_name)
            stock_data = stock.history(period="1d")
            stock_price = stock_data["Close"].values[0]

            """Get the volatility of a stock over a given period"""
            data = yf.download(stock_name, period="1y", interval="1d")
            data['Log Return'] = np.log(data['Adj Close'] / data['Adj Close'].shift(1))
            volatility = data['Log Return'].std()
            volatility = volatility * np.sqrt(252)
            print(stock_name)
            print(volatility)
            return f"The stock price is: {stock_price} and volatility is: {volatility} ."
        except:
            return("Stock data not found. Please try again.")

    # Example dummy function hard coded to trade a stock
    # with a specific action (buy or sell)
    def trade_stock(self, action, stock_name, price):
        """Trade a stock"""
        assert action in ["buy", "sell"]
        print(f"Traded {stock_name} at {price} with action {action}")
        return f"Traded {stock_name} at {price} with action {action}"

    if __name__ == "__main__":
        assistant = GPTAssistant()
        while True:
            user_input = input("User: ")
            if user_input.lower() == "exit":
                break
            assistant_response = assistant.conversation(user_input)
            print("Assistant:", assistant_response)
