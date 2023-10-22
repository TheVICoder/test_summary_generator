from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.checkbox import CheckBox
from kivy.properties import ObjectProperty
from kivy.config import Config
import configparser

# Set window size
Config.set('graphics', 'width', '300')
Config.set('graphics', 'height', '500')

# Read settings.ini
config = configparser.ConfigParser()
config.read('settings.ini')

ot_number = int(config['ListValues']['ot_number'])
report_title = int(config['ListValues']['report_title'])
severity = int(config['ListValues']['severity'])


class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        label = Label(text='Welcome! Create your next summary now', color=(0, 0.6, 1, 1), font_size=24)
        button = Button(text='Start', on_press=self.on_start_pressed, background_color=(0, 0.6, 1, 1))
        layout.add_widget(label)
        layout.add_widget(button)
        self.add_widget(layout)

    def on_start_pressed(self, instance):
        self.manager.current = 'details'


class DetailsScreen(Screen):
    project_spinner = ObjectProperty()
    version_input = ObjectProperty()
    test_pack_input = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.project_spinner = Spinner(text='Select Project', values=('SN', 'GC', 'ER'), background_color=(0.1, 0.1, 0.1, 1))
        self.version_input = TextInput(hint_text='Version Number', background_color=(0.1, 0.1, 0.1, 1),
                                      foreground_color=(0, 0.6, 1, 1))
        self.test_pack_input = TextInput(hint_text='Test Pack Completed', background_color=(0.1, 0.1, 0.1, 1),
                                        foreground_color=(0, 0.6, 1, 1))
        next_button = Button(text='Next', on_press=self.on_next_pressed, background_color=(0, 0.6, 1, 1))
        layout.add_widget(self.project_spinner)
        layout.add_widget(self.version_input)
        layout.add_widget(self.test_pack_input)
        layout.add_widget(next_button)
        self.add_widget(layout)

        self.project = None
        self.version = None
        self.test_pack = None

    def on_next_pressed(self, instance):
        self.project = self.project_spinner.text
        self.version = self.version_input.text
        self.test_pack = self.test_pack_input.text

        subject = f"{self.project} {self.version} {self.test_pack}"
        self.manager.current = 'bugs'
        self.manager.get_screen('bugs').set_subject(subject)

class BugsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        defects_label = Label(text='Defects', color=(0, 0.6, 1, 1), font_size=24)
        defects_list = TextInput(readonly=True, height=100, background_color=(0.1, 0.1, 0.1, 1),
                                 foreground_color=(0, 0.6, 1, 1))
        self.bug_report_input = TextInput(hint_text='Bug Report', background_color=(0.1, 0.1, 0.1, 1),
                                          foreground_color=(0, 0.6, 1, 1))
        self.existing_checkbox = CheckBox(group='bug_type', active=True, color=(0, 0.6, 1, 1))
        existing_label = Label(text='Existing', color=(0, 0.6, 1, 1))
        new_checkbox = CheckBox(group='bug_type', color=(0, 0.6, 1, 1))
        new_label = Label(text='New', color=(0, 0.6, 1, 1))
        add_button = Button(text='Add', on_press=self.on_add_pressed, background_color=(0, 0.6, 1, 1))
        down_button = Button(text='Write to File', on_press=self.on_down_pressed, background_color=(0, 0.6, 1, 1))
        layout.add_widget(defects_label)
        layout.add_widget(defects_list)
        layout.add_widget(self.bug_report_input)
        layout.add_widget(self.existing_checkbox)
        layout.add_widget(existing_label)
        layout.add_widget(new_checkbox)
        layout.add_widget(new_label)
        layout.add_widget(add_button)
        layout.add_widget(down_button)
        self.add_widget(layout)

        self.subject = ''
        self.existing_bugs = []
        self.new_bugs = []

    def set_subject(self, subject):
        self.subject = subject

    def on_add_pressed(self, instance):
        try:
            bug_report = self.bug_report_input.text
            print("completed data import")
            text_list = bug_report.split('","')
            print("completed splitting to list")

            if len(text_list) >= 3:  # Check if there are at least 3 elements in the list
                OT_number = text_list[ot_number]
                bug_title = text_list[report_title]
                criticality = text_list[severity]
                modified_text = f"{OT_number} - {bug_title} - {criticality}"
                print(modified_text)  # Check the modified text

                if self.existing_checkbox.active:
                    self.existing_bugs.append(modified_text)
                else:
                    self.new_bugs.append(modified_text)
                self.refresh_defects_list()

            else:
                raise Exception("Not enough elements in the list")

        except Exception as e:
            print(e)  # You can handle the exception as needed

    def on_down_pressed(self, instance):
        with open(f"{self.subject}.txt", 'w') as file:
            file.write(f"Subject: {self.subject}\n")
            file.write("Existing Bugs:\n")
            file.write('\n'.join(self.existing_bugs))
            file.write("\nNew Bugs:\n")
            file.write('\n'.join(self.new_bugs))


class SummaryApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(DetailsScreen(name='details'))
        sm.add_widget(BugsScreen(name='bugs'))
        return sm


if __name__ == '__main__':
    SummaryApp().run()
