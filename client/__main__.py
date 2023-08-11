#!/usr/bin/python
##-------------------------------##
## Barracuda Client              ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
import asyncio

from kivy.app import App
from kivy.uix.widget import Widget


## Classes
class BarracudaApp(App):
    """Barracuda client implementation using Kivy GUI framework"""

    # -Instance Methods
    def build(self) -> Widget:
        self.title = "Barracuda"
        return Widget()


## Body
asyncio.run(
    BarracudaApp().async_run()
)
