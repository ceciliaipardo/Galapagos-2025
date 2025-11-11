from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from translations import translator

class Welcome(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class TestApp(App):
    # Create observable string properties for all translatable text
    welcome_text = StringProperty()
    username_text = StringProperty()
    password_text = StringProperty()
    login_text = StringProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.translator = translator
        self.update_text_properties()
    
    def update_text_properties(self):
        """Update all text properties with current language"""
        self.welcome_text = self.translator.get_text('welcome')
        self.username_text = self.translator.get_text('username')
        self.password_text = self.translator.get_text('password')
        self.login_text = self.translator.get_text('login')
    
    def build(self):
        # Load the test KV file
        return Builder.load_file('test_translation.kv')

    def toggle_language(self):
        """Toggle between English and Spanish and update all UI text"""
        translator.toggle_language()
        self.update_text_properties()

# run the application
if __name__=='__main__':
    TestApp().run()
