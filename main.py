from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import sqlite3

Window.clearcolor = (0.96, 0.91, 0.78, 1)  # Parchment

class MiniSOP(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.12)
        header.add_widget(Label(text='📖', font_size=42, size_hint_x=0.2))
        header.add_widget(Label(text='Mini SOP Searcher', font_size=26, bold=True, color=(0.545, 0.271, 0.075, 1)))
        self.root.add_widget(header)
        
        # Search Bar
        search_box = BoxLayout(size_hint_y=0.15, spacing=10)
        self.search_input = TextInput(hint_text='Search words or phrase...', multiline=False, font_size=18)
        search_btn = Button(text='SEARCH', background_color=(0.545, 0.271, 0.075, 1), color=(1,1,1,1), size_hint_x=0.35)
        search_btn.bind(on_press=self.do_search)
        search_box.add_widget(self.search_input)
        search_box.add_widget(search_btn)
        self.root.add_widget(search_box)
        
        # Counter
        self.counter = Label(text="EXACT MATCHES: 00000", font_size=18, size_hint_y=0.08, color=(0, 0.4, 0, 1))
        self.root.add_widget(self.counter)
        
        # Results
        self.scroll = ScrollView()
        self.layout = GridLayout(cols=1, spacing=12, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scroll.add_widget(self.layout)
        self.root.add_widget(self.scroll)
        
        # Pagination
        pag = BoxLayout(size_hint_y=0.1, spacing=20)
        self.prev_btn = Button(text="← Previous", disabled=True)
        self.prev_btn.bind(on_press=self.prev_page)
        self.page_label = Label(text="Page 1", font_size=18)
        self.next_btn = Button(text="Next →", disabled=True)
        self.next_btn.bind(on_press=self.next_page)
        pag.add_widget(self.prev_btn)
        pag.add_widget(self.page_label)
        pag.add_widget(self.next_btn)
        self.root.add_widget(pag)
        
        return self.root
    
    def do_search(self, instance):
        query = self.search_input.text.strip().lower()
        if not query:
            return
        
        instance.background_color = (0, 0, 0, 1)
        instance.color = (1, 0, 0, 1)
        instance.text = "SEARCHING..."
        
        self.layout.clear_widgets()
        
        conn = sqlite3.connect("egw_search.db")
        self.all_results = conn.execute("SELECT book_title, text FROM sentences WHERE text LIKE ? LIMIT 800", (f"%{query}%",)).fetchall()
        conn.close()
        
        self.current_page = 0
        self.display_page()
        
        instance.background_color = (0.545, 0.271, 0.075, 1)
        instance.color = (1,1,1,1)
        instance.text = "SEARCH"
    
    def display_page(self):
        self.layout.clear_widgets()
        start = self.current_page * 12
        page_results = self.all_results[start:start+12]
        
        for r in page_results:
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=110)
            box.add_widget(Label(text=r[0], font_size=16, color=(0.545, 0.271, 0.075, 1), halign='left'))
            box.add_widget(Label(text=r[1], font_size=15, halign='left', text_size=(self.root.width-50, None)))
            self.layout.add_widget(box)
        
        self.counter.text = f"EXACT MATCHES: {len(self.all_results):05d}"
        total_pages = (len(self.all_results) - 1) // 12 + 1
        self.page_label.text = f"Page {self.current_page + 1} of {total_pages}"
        
        self.prev_btn.disabled = self.current_page == 0
        self.next_btn.disabled = (self.current_page + 1) * 12 >= len(self.all_results)
    
    def next_page(self, instance):
        self.current_page += 1
        self.display_page()
    
    def prev_page(self, instance):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

if __name__ == '__main__':
    MiniSOP().run()