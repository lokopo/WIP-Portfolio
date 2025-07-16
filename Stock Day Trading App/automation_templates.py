"""
Automation Templates for Trading Platforms
Pre-configured automation sequences for common trading platform interactions.
"""

from typing import List, Dict
from dataclasses import dataclass
from main import Command, CommandType

@dataclass
class AutomationTemplate:
    name: str
    description: str
    platform: str
    commands: List[Command]

class AutomationTemplates:
    """Collection of automation templates for different trading platforms"""
    
    @staticmethod
    def robinhood_buy_template(symbol: str, quantity: int) -> AutomationTemplate:
        """Template for buying stock on Robinhood"""
        return AutomationTemplate(
            name="Robinhood Buy Order",
            description=f"Automated buy order for {quantity} shares of {symbol}",
            platform="Robinhood",
            commands=[
                # Click search box
                Command(type=CommandType.CLICK, x=200, y=100),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Type symbol
                Command(type=CommandType.TYPE, text=symbol),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Press Enter to search
                Command(type=CommandType.HOTKEY, keys="enter"),
                Command(type=CommandType.DELAY, seconds=2),
                
                # Click Buy button
                Command(type=CommandType.CLICK, x=300, y=400),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Type quantity
                Command(type=CommandType.TYPE, text=str(quantity)),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Click Review Order
                Command(type=CommandType.CLICK, x=400, y=500),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Click Submit Order
                Command(type=CommandType.CLICK, x=450, y=550),
            ]
        )
    
    @staticmethod
    def robinhood_sell_template(symbol: str, quantity: int) -> AutomationTemplate:
        """Template for selling stock on Robinhood"""
        return AutomationTemplate(
            name="Robinhood Sell Order",
            description=f"Automated sell order for {quantity} shares of {symbol}",
            platform="Robinhood",
            commands=[
                # Click search box
                Command(type=CommandType.CLICK, x=200, y=100),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Type symbol
                Command(type=CommandType.TYPE, text=symbol),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Press Enter to search
                Command(type=CommandType.HOTKEY, keys="enter"),
                Command(type=CommandType.DELAY, seconds=2),
                
                # Click Sell button
                Command(type=CommandType.CLICK, x=400, y=400),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Type quantity
                Command(type=CommandType.TYPE, text=str(quantity)),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Click Review Order
                Command(type=CommandType.CLICK, x=400, y=500),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Click Submit Order
                Command(type=CommandType.CLICK, x=450, y=550),
            ]
        )
    
    @staticmethod
    def td_ameritrade_buy_template(symbol: str, quantity: int) -> AutomationTemplate:
        """Template for buying stock on TD Ameritrade"""
        return AutomationTemplate(
            name="TD Ameritrade Buy Order",
            description=f"Automated buy order for {quantity} shares of {symbol}",
            platform="TD Ameritrade",
            commands=[
                # Click Trade tab
                Command(type=CommandType.CLICK, x=150, y=50),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Click Symbol field
                Command(type=CommandType.CLICK, x=200, y=150),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Type symbol
                Command(type=CommandType.TYPE, text=symbol),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Press Tab to move to quantity
                Command(type=CommandType.HOTKEY, keys="tab"),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Type quantity
                Command(type=CommandType.TYPE, text=str(quantity)),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Click Buy button
                Command(type=CommandType.CLICK, x=300, y=300),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Click Review Order
                Command(type=CommandType.CLICK, x=350, y=400),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Click Submit Order
                Command(type=CommandType.CLICK, x=400, y=450),
            ]
        )
    
    @staticmethod
    def etrade_buy_template(symbol: str, quantity: int) -> AutomationTemplate:
        """Template for buying stock on E*TRADE"""
        return AutomationTemplate(
            name="E*TRADE Buy Order",
            description=f"Automated buy order for {quantity} shares of {symbol}",
            platform="E*TRADE",
            commands=[
                # Click Trading tab
                Command(type=CommandType.CLICK, x=200, y=60),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Click Symbol field
                Command(type=CommandType.CLICK, x=250, y=200),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Type symbol
                Command(type=CommandType.TYPE, text=symbol),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Press Enter to search
                Command(type=CommandType.HOTKEY, keys="enter"),
                Command(type=CommandType.DELAY, seconds=2),
                
                # Click Buy button
                Command(type=CommandType.CLICK, x=300, y=350),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Click Quantity field
                Command(type=CommandType.CLICK, x=350, y=400),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Type quantity
                Command(type=CommandType.TYPE, text=str(quantity)),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Click Preview Order
                Command(type=CommandType.CLICK, x=400, y=500),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Click Place Order
                Command(type=CommandType.CLICK, x=450, y=550),
            ]
        )
    
    @staticmethod
    def webull_buy_template(symbol: str, quantity: int) -> AutomationTemplate:
        """Template for buying stock on Webull"""
        return AutomationTemplate(
            name="Webull Buy Order",
            description=f"Automated buy order for {quantity} shares of {symbol}",
            platform="Webull",
            commands=[
                # Click search icon
                Command(type=CommandType.CLICK, x=100, y=100),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Type symbol
                Command(type=CommandType.TYPE, text=symbol),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Press Enter to search
                Command(type=CommandType.HOTKEY, keys="enter"),
                Command(type=CommandType.DELAY, seconds=2),
                
                # Click Buy button
                Command(type=CommandType.CLICK, x=250, y=300),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Click Quantity field
                Command(type=CommandType.CLICK, x=300, y=350),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Type quantity
                Command(type=CommandType.TYPE, text=str(quantity)),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Click Review Order
                Command(type=CommandType.CLICK, x=350, y=450),
                Command(type=CommandType.DELAY, seconds=1),
                
                # Click Submit Order
                Command(type=CommandType.CLICK, x=400, y=500),
            ]
        )
    
    @staticmethod
    def generic_refresh_template() -> AutomationTemplate:
        """Template for refreshing trading platform data"""
        return AutomationTemplate(
            name="Refresh Data",
            description="Refresh trading platform data",
            platform="Generic",
            commands=[
                # Press F5 to refresh
                Command(type=CommandType.HOTKEY, keys="f5"),
                Command(type=CommandType.DELAY, seconds=2),
                
                # Or click refresh button (common location)
                Command(type=CommandType.CLICK, x=50, y=50),
                Command(type=CommandType.DELAY, seconds=2),
            ]
        )
    
    @staticmethod
    def generic_close_popup_template() -> AutomationTemplate:
        """Template for closing popup dialogs"""
        return AutomationTemplate(
            name="Close Popup",
            description="Close popup dialog or notification",
            platform="Generic",
            commands=[
                # Try clicking common close button locations
                Command(type=CommandType.CLICK, x=800, y=50),  # Top-right corner
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Or press Escape
                Command(type=CommandType.HOTKEY, keys="escape"),
                Command(type=CommandType.DELAY, seconds=0.5),
                
                # Or click center of screen to dismiss
                Command(type=CommandType.CLICK, x=400, y=300),
                Command(type=CommandType.DELAY, seconds=0.5),
            ]
        )
    
    @staticmethod
    def get_all_templates() -> Dict[str, List[AutomationTemplate]]:
        """Get all available automation templates organized by platform"""
        return {
            "Robinhood": [
                AutomationTemplates.robinhood_buy_template("AAPL", 100),
                AutomationTemplates.robinhood_sell_template("AAPL", 100),
            ],
            "TD Ameritrade": [
                AutomationTemplates.td_ameritrade_buy_template("AAPL", 100),
            ],
            "E*TRADE": [
                AutomationTemplates.etrade_buy_template("AAPL", 100),
            ],
            "Webull": [
                AutomationTemplates.webull_buy_template("AAPL", 100),
            ],
            "Generic": [
                AutomationTemplates.generic_refresh_template(),
                AutomationTemplates.generic_close_popup_template(),
            ]
        }
    
    @staticmethod
    def customize_template(template: AutomationTemplate, **kwargs) -> AutomationTemplate:
        """Customize a template with specific parameters"""
        # Create a copy of the template
        customized_commands = []
        
        for command in template.commands:
            if command.type == CommandType.TYPE:
                # Replace placeholder text
                if command.text == "AAPL":
                    command.text = kwargs.get('symbol', 'AAPL')
                elif command.text == "100":
                    command.text = str(kwargs.get('quantity', 100))
            
            customized_commands.append(command)
        
        return AutomationTemplate(
            name=template.name,
            description=template.description,
            platform=template.platform,
            commands=customized_commands
        )

# Example usage functions
def create_buy_order_sequence(symbol: str, quantity: int, platform: str = "Robinhood") -> List[Command]:
    """Create a buy order sequence for the specified platform"""
    templates = AutomationTemplates.get_all_templates()
    
    if platform in templates:
        for template in templates[platform]:
            if "Buy" in template.name:
                customized = AutomationTemplates.customize_template(
                    template, symbol=symbol, quantity=quantity
                )
                return customized.commands
    
    # Fallback to generic template
    return AutomationTemplates.generic_refresh_template().commands

def create_sell_order_sequence(symbol: str, quantity: int, platform: str = "Robinhood") -> List[Command]:
    """Create a sell order sequence for the specified platform"""
    templates = AutomationTemplates.get_all_templates()
    
    if platform in templates:
        for template in templates[platform]:
            if "Sell" in template.name:
                customized = AutomationTemplates.customize_template(
                    template, symbol=symbol, quantity=quantity
                )
                return customized.commands
    
    # Fallback to generic template
    return AutomationTemplates.generic_refresh_template().commands