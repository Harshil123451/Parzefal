import pyttsx3
import speech_recognition as sr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import nltk 
from sklearn.model_selection import train_test_split
import random
import warnings
warnings.simplefilter('ignore')
import requests
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
import json
import yfinance as yf  # For stock data

# nltk.download("punkt")

def speak(text): 
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print("")
    print(f"==> Parzefal AI : {text}")
    print("")
    Id = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0'
    engine.setProperty('voices',Id)
    engine.say(text=text)
    engine.runAndWait()
    
def speechrecognition():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening.....")
        r.pause_threshold = 1
        audio = r.listen(source,0,8)
        
    try:
        print("Recognizing....")
        query = r.recognize_google(audio,language="en")
        return query.lower()
    
    except:
        return ""

def MainExecution(query):
    Query = str(query).lower()
    
    if "hello" in Query:
        speak("Hello, I am Parzefal. How may I help you?")
        
    elif "bye" in Query:
        speak("Bye, Have a nice day!")
        
    elif "time" in Query:
        if "in" in Query or "at" in Query:
            # Extract location from query
            location = extract_location(Query)
            if location:
                get_time(location)
            else:
                speak("Please specify a location for the time check.")
        else:
            # Get local time
            get_time()
        
    elif any(word in Query for word in ["game", "games", "gaming"]):
        if "mobile" in Query:
            recommendation = get_mobile_game_recommendation()
        elif "free" in Query:
            recommendation = get_free_games_recommendation()
        else:
            recommendation = get_game_recommendation()
        speak(recommendation)
    elif any(word in Query for word in ["career", "job", "professional", "resume", "interview"]):
        if "trends" in Query or "opportunities" in Query:
            advice = get_job_market_trends()
        elif "skills" in Query or "learn" in Query:
            advice = get_skill_development_advice()
        else:
            advice = get_career_advice()
        speak(advice)
    
            

intents = {
    "greetings": {
        "patterns": ["hello", "hi", "hey", "howdy", "greetings", "good morning", "good afternoon", "good evening", "hi there", "hey there", "what's up", "hello there"],
        "responses": ["Hello! How can I assist you?", "Hi there!", "Hey! What can I do for you?", "Howdy! What brings you here?", "Greetings! How may I help you?", "Good morning! How can I be of service?", "Good afternoon! What do you need assistance with?", "Good evening! How may I assist you?", "Hey there! How can I help?", "Hi! What's on your mind?", "Hello there! How can I assist you today?"]
    },
    "goodbye": {
        "patterns": ["bye", "see you later", "goodbye", "farewell", "take care", "until next time", "bye bye", "catch you later", "have a good one", "so long"],
        "responses": ["Goodbye!", "See you later!", "Have a great day!", "Farewell! Take care.", "Goodbye! Until next time.", "Take care! Have a wonderful day.", "Bye bye!", "Catch you later!", "Have a good one!", "So long!"]
    },
    "gratitude": {
        "patterns": ["thank you", "thanks", "appreciate it", "thank you so much", "thanks a lot", "much appreciated"],
        "responses": ["You're welcome!", "Happy to help!", "Glad I could assist.", "Anytime!", "You're welcome! Have a great day.", "No problem!"]
    },
    "apologies": {
        "patterns": ["sorry", "my apologies", "apologize", "I'm sorry"],
        "responses": ["No problem at all.", "It's alright.", "No need to apologize.", "That's okay.", "Don't worry about it.", "Apology accepted."]
    },
    "positive_feedback": {
        "patterns": ["great job", "well done", "awesome", "fantastic", "amazing work", "excellent"],
        "responses": ["Thank you! I appreciate your feedback.", "Glad to hear that!", "Thank you for the compliment!", "I'm glad I could meet your expectations.", "Your words motivate me!", "Thank you for your kind words."]
    },
    "negative_feedback": {
        "patterns": ["not good", "disappointed", "unsatisfied", "poor service", "needs improvement", "could be better"],
        "responses": ["I'm sorry to hear that. Can you please provide more details so I can assist you better?", "I apologize for the inconvenience. Let me help resolve the issue.", "I'm sorry you're not satisfied. Please let me know how I can improve.", "Your feedback is valuable. I'll work on improving."]
    },
    "weather": {
        "patterns": ["what's the weather like in", "weather forecast for", "temperature in", "weather in", "how's the weather in", "tell me the weather in"],
        "responses": ["Let me check the weather information for you."]
    },
    "help": {
        "patterns": ["help", "can you help me?", "I need assistance", "support"],
        "responses": ["Sure, I'll do my best to assist you.", "Of course, I'm here to help!", "How can I assist you?", "I'll help you with your query."]
    },
    "time": {
        "patterns": ["what's the time", "current time", "time please", "what time is it", "tell me the time", "what's the time in", "time in"],
        "responses": ["Let me check the time for you."]
    },
    "jokes": {
        "patterns": ["tell me a joke", "joke please", "got any jokes?", "make me laugh"],
        "responses": ["Why don't we ever tell secrets on a farm? Because the potatoes have eyes and the corn has ears!", "What do you get when you cross a snowman and a vampire? Frostbite!", "Why was the math book sad? Because it had too many problems!"]
    },
    "music": {
        "patterns": ["play music", "music please", "song recommendation", "music suggestion"],
        "responses": ["Sure, playing some music for you!", "Here's a song you might like: [song_name]", "How about some music?"]
    },
    "food": {
        "patterns": ["recommend a restaurant", "food places nearby", "what's good to eat?", "restaurant suggestion"],
        "responses": ["Sure, here are some recommended restaurants: [restaurant_names]", "Hungry? Let me find some good food places for you!", "I can suggest some great places to eat nearby."]
    },
    "news": {
        "patterns": ["latest news", "news updates", "what's happening?", "current events"],
        "responses": ["Let me fetch the latest news for you.", "Here are the top headlines: [news_headlines]", "Stay updated with the latest news!"]
    },
    "movies": {
        "patterns": ["movie suggestions", "recommend a movie", "what should I watch?", "best movies"],
        "responses": ["How about watching [movie_name]?", "Here's a movie suggestion for you.", "Let me recommend some great movies!"]
    },
    "sports": {
        "patterns": ["sports news", "score updates", "latest sports events", "upcoming games"],
        "responses": ["I'll get you the latest sports updates.", "Stay updated with the current sports events!", "Let me check the sports scores for you."]
    },
    "gaming": {
        "patterns": ["video game recommendations", "best games to play", "recommend a game", "gaming suggestions"],
        "responses": ["How about trying out [game_name]?", "Here are some gaming suggestions for you!", "Let me recommend some fun games to play!"]
    },
        "tech_support": {
        "patterns": ["technical help", "computer issues", "troubleshooting", "IT support"],
        "responses": ["I can assist with technical issues. What problem are you facing?", "Let's troubleshoot your technical problem together.", "Tell me about the technical issue you're experiencing."]
    },
    "book_recommendation": {
        "patterns": ["recommend a book", "good books to read", "book suggestions", "what should I read?"],
        "responses": ["How about reading [book_title]?", "I've got some great book recommendations for you!", "Let me suggest some interesting books for you to read."]
    },
    "fitness_tips": {
        "patterns": ["fitness advice", "workout tips", "exercise suggestions", "healthy habits"],
        "responses": ["Staying fit is important! Here are some fitness tips: [fitness_tips]", "I can help you with workout suggestions and fitness advice.", "Let me provide some exercise recommendations for you."]
    },
    "travel_recommendation": {
        "patterns": ["travel suggestions", "places to visit", "recommend a destination", "travel ideas"],
        "responses": ["Looking for travel recommendations? Here are some great destinations: [travel_destinations]", "I can suggest some amazing places for your next travel adventure!", "Let me help you with travel destination ideas."]
    },
    "education": {
        "patterns": ["learning resources", "study tips", "education advice", "academic help"],
        "responses": ["I can assist with educational queries. What subject are you studying?", "Let's explore learning resources together.", "Tell me about your educational goals or questions."]
    },
    "pet_advice": {
        "patterns": ["pet care tips", "animal advice", "pet health", "taking care of pets"],
        "responses": ["Pets are wonderful! Here are some pet care tips: [pet_care_tips]", "I can provide advice on pet health and care.", "Let's talk about your pet and their well-being."]
    },
    "shopping": {
        "patterns": ["online shopping", "buying something", "shopping advice", "product recommendations"],
        "responses": ["I can help you with online shopping. What are you looking to buy?", "Let's find the perfect item for you!", "Tell me what you're interested in purchasing."]
    },
    "career_advice": {
        "patterns": [
            "career advice", "job search help", "career guidance", 
            "career change advice", "professional development",
            "resume tips", "interview tips", "job hunting help",
            "career path", "career development", "job advice"
        ],
        "responses": [
            "Let me help you with some career advice.",
            "Here's some professional guidance for you.",
            "I'll share some career tips with you."
        ]
    },
    "relationship_advice": {
        "patterns": ["relationship help", "love advice", "dating tips", "relationship problems"],
        "responses": ["Relationships can be complex. How can I assist you?", "I can offer advice on relationships and dating.", "Tell me about your relationship situation."]
    },
    "mental_health": {
        "patterns": ["mental health support", "coping strategies", "stress relief tips", "emotional well-being"],
        "responses": ["Mental health is important. How can I support you?", "I can provide guidance for managing stress and emotions.", "Let's talk about strategies for maintaining mental well-being."]
    },
    "language_learning": {
        "patterns": ["language learning tips", "language practice", "learning new languages", "language study advice"],
        "responses": ["Learning a new language can be exciting! How can I assist you?", "I can help with language learning tips and practice.", "Tell me which language you're interested in learning."]
    },
    "finance_advice": {
        "patterns": ["financial advice", "money tips", "investment advice", "saving tips", "budgeting help", "stock market advice", "cryptocurrency advice"],
        "responses": ["Let me help you with some financial advice.", "Here's some financial guidance.", "I'll share some financial tips with you."]
    },
    "movie_recommendation": {
        "patterns": ["recommend a movie", "suggest a movie", "what movie should i watch", "good movies to watch", "movie recommendation"],
        "responses": ["Let me find a good movie for you!", "I'll suggest a movie you might like!", "Here's a movie recommendation:"]
    },
    "song_recommendation": {
        "patterns": ["recommend a song", "suggest a song", "what should i listen to", "good songs", "music recommendation"],
        "responses": ["Let me find some good music for you!", "Here's a song you might like!", "Check out this song:"]
    },
    "book_recommendation": {
        "patterns": ["recommend a book", "suggest a book", "what should i read", "good books", "book recommendation"],
        "responses": ["Let me find a good book for you!", "Here's a book you might enjoy!", "I recommend this book:"]
    },
    "stock_price": {
        "patterns": ["stock price of", "how much is stock", "stock value", "check stock", "stock market price"],
        "responses": ["Let me check that stock price for you.", "I'll get the current stock value.", "Let me look up that stock information."]
    },
    "game_recommendation": {
        "patterns": [
            "recommend a game", "suggest a game", "what game should i play", 
            "good games to play", "game recommendation", "video game suggestion",
            "what's a fun game", "popular games", "new games to try"
        ],
        "responses": [
            "Let me find a great game for you!", 
            "Here's a game you might enjoy!",
            "I've got a game recommendation for you!"
        ]
    },
}
    
training_data = []
labels = [] 

for  intent , data in intents.items():
    for pattern in data['patterns']:
        training_data.append(pattern.lower())
        labels.append(intent)

# print(training_data)
# print(labels)
  
vectorizer = TfidfVectorizer(tokenizer=nltk.word_tokenize,stop_words="english",max_df=0.8,min_df=1)  
X_train = vectorizer.fit_transform(training_data)
X_train,X_test,Y_train,Y_test = train_test_split(X_train,labels,test_size=0.4,random_state=42,stratify=labels)

model =SVC(kernel='linear', probability=True, C=1.0)
model.fit(X_train , Y_train)

predictions = model.predict(X_test)

def predict_intent(user_input):
    user_input = user_input.lower()
    input_vector = vectorizer.transform([user_input])
    intent = model.predict(input_vector)[0]
    return intent

def extract_city(user_input):
    # List of weather-related keywords to remove
    weather_keywords = ["what's", "what is", "the", "weather", "like", "in", "forecast", "for", "temperature", "tell", "me", "how's", "hows"]
    
    # Split the input into words
    words = user_input.lower().split()
    
    # Remove weather-related keywords
    city_words = [word for word in words if word not in weather_keywords]
    
    # Join remaining words to form city name
    return " ".join(city_words).strip()

def get_weather(city):
    api_key = "26d7cee0d2b74fc4a7193452241611"  # Replace with your WeatherAPI.com key
    base_url = "http://api.weatherapi.com/v1/current.json"
    
    params = {
        "key": api_key,
        "q": city,
        "aqi": "no"  # We don't need air quality data for basic weather
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            temp = data["current"]["temp_c"]
            condition = data["current"]["condition"]["text"]
            humidity = data["current"]["humidity"]
            feels_like = data["current"]["feelslike_c"]
            return f"The temperature in {city} is {temp}°C, feels like {feels_like}°C, with {condition}. The humidity is {humidity}%"
        else:
            return "Sorry, I couldn't fetch the weather information for that city."
    except Exception as e:
        return "Sorry, there was an error getting the weather information."

def extract_location(query):
    # Words to remove from the query to get the location
    remove_words = [
        "what", "what's", "whats", "time", "in", "at", "the", "tell", "me", 
        "current", "now", "please", "timezone", "zone"
    ]
    
    # Split the query into words and remove the unwanted ones
    words = query.lower().split()
    location_words = [word for word in words if word not in remove_words]
    
    # Join the remaining words to form the location
    location = " ".join(location_words).strip()
    return location if location else None

def get_time(location=None):
    try:
        # Comprehensive dictionary of cities and their timezones
        timezone_map = {
            # Asia
            "india": "Asia/Kolkata",
            "delhi": "Asia/Kolkata",
            "mumbai": "Asia/Kolkata",
            "kolkata": "Asia/Kolkata",
            "bangalore": "Asia/Kolkata",
            "chennai": "Asia/Kolkata",
            "tokyo": "Asia/Tokyo",
            "japan": "Asia/Tokyo",
            "osaka": "Asia/Tokyo",
            "beijing": "Asia/Shanghai",
            "shanghai": "Asia/Shanghai",
            "china": "Asia/Shanghai",
            "hong kong": "Asia/Hong_Kong",
            "singapore": "Asia/Singapore",
            "seoul": "Asia/Seoul",
            "bangkok": "Asia/Bangkok",
            "manila": "Asia/Manila",
            "kuala lumpur": "Asia/Kuala_Lumpur",
            "jakarta": "Asia/Jakarta",
            "hanoi": "Asia/Ho_Chi_Minh",
            "taipei": "Asia/Taipei",
            "dubai": "Asia/Dubai",
            "abu dhabi": "Asia/Dubai",
            "riyadh": "Asia/Riyadh",
            "doha": "Asia/Qatar",
            "muscat": "Asia/Muscat",
            "karachi": "Asia/Karachi",
            "dhaka": "Asia/Dhaka",
            "yangon": "Asia/Yangon",
            "kathmandu": "Asia/Kathmandu",
            "colombo": "Asia/Colombo",
            "kabul": "Asia/Kabul",
            "tehran": "Asia/Tehran",
            "baghdad": "Asia/Baghdad",
            "jerusalem": "Asia/Jerusalem",
            "beirut": "Asia/Beirut",
            
            # Europe
            "london": "Europe/London",
            "paris": "Europe/Paris",
            "berlin": "Europe/Berlin",
            "rome": "Europe/Rome",
            "madrid": "Europe/Madrid",
            "lisbon": "Europe/Lisbon",
            "amsterdam": "Europe/Amsterdam",
            "brussels": "Europe/Brussels",
            "vienna": "Europe/Vienna",
            "moscow": "Europe/Moscow",
            "stockholm": "Europe/Stockholm",
            "oslo": "Europe/Oslo",
            "copenhagen": "Europe/Copenhagen",
            "helsinki": "Europe/Helsinki",
            "warsaw": "Europe/Warsaw",
            "prague": "Europe/Prague",
            "budapest": "Europe/Budapest",
            "athens": "Europe/Athens",
            "bucharest": "Europe/Bucharest",
            "kiev": "Europe/Kiev",
            "minsk": "Europe/Minsk",
            "istanbul": "Europe/Istanbul",
            "zurich": "Europe/Zurich",
            "geneva": "Europe/Zurich",
            "dublin": "Europe/Dublin",
            "edinburgh": "Europe/London",
            "glasgow": "Europe/London",
            
            # North America
            "new york": "America/New_York",
            "washington": "America/New_York",
            "boston": "America/New_York",
            "chicago": "America/Chicago",
            "los angeles": "America/Los_Angeles",
            "san francisco": "America/Los_Angeles",
            "las vegas": "America/Los_Angeles",
            "seattle": "America/Los_Angeles",
            "denver": "America/Denver",
            "phoenix": "America/Phoenix",
            "houston": "America/Chicago",
            "dallas": "America/Chicago",
            "miami": "America/New_York",
            "toronto": "America/Toronto",
            "vancouver": "America/Vancouver",
            "montreal": "America/Montreal",
            "ottawa": "America/Toronto",
            "mexico city": "America/Mexico_City",
            "havana": "America/Havana",
            "panama city": "America/Panama",
            
            # South America
            "sao paulo": "America/Sao_Paulo",
            "rio de janeiro": "America/Sao_Paulo",
            "brasilia": "America/Sao_Paulo",
            "buenos aires": "America/Argentina/Buenos_Aires",
            "lima": "America/Lima",
            "bogota": "America/Bogota",
            "santiago": "America/Santiago",
            "caracas": "America/Caracas",
            "montevideo": "America/Montevideo",
            "asuncion": "America/Asuncion",
            "la paz": "America/La_Paz",
            "quito": "America/Guayaquil",
            
            # Africa
            "cairo": "Africa/Cairo",
            "lagos": "Africa/Lagos",
            "johannesburg": "Africa/Johannesburg",
            "nairobi": "Africa/Nairobi",
            "casablanca": "Africa/Casablanca",
            "tunis": "Africa/Tunis",
            "addis ababa": "Africa/Addis_Ababa",
            "dar es salaam": "Africa/Dar_es_Salaam",
            "khartoum": "Africa/Khartoum",
            "accra": "Africa/Accra",
            "algiers": "Africa/Algiers",
            "dakar": "Africa/Dakar",
            
            # Oceania
            "sydney": "Australia/Sydney",
            "melbourne": "Australia/Melbourne",
            "brisbane": "Australia/Brisbane",
            "perth": "Australia/Perth",
            "adelaide": "Australia/Adelaide",
            "auckland": "Pacific/Auckland",
            "wellington": "Pacific/Auckland",
            "christchurch": "Pacific/Auckland",
            "suva": "Pacific/Fiji",
            "port moresby": "Pacific/Port_Moresby",
            
            # Countries (for general queries)
            "united states": "America/New_York",
            "uk": "Europe/London",
            "united kingdom": "Europe/London",
            "australia": "Australia/Sydney",
            "new zealand": "Pacific/Auckland",
            "canada": "America/Toronto",
            "germany": "Europe/Berlin",
            "france": "Europe/Paris",
            "italy": "Europe/Rome",
            "spain": "Europe/Madrid",
            "russia": "Europe/Moscow",
            "brazil": "America/Sao_Paulo",
            "argentina": "America/Argentina/Buenos_Aires",
            "south africa": "Africa/Johannesburg",
            "egypt": "Africa/Cairo",
            "saudi arabia": "Asia/Riyadh",
            "uae": "Asia/Dubai",
            "pakistan": "Asia/Karachi",
            "bangladesh": "Asia/Dhaka",
            "thailand": "Asia/Bangkok",
            "vietnam": "Asia/Ho_Chi_Minh",
            "philippines": "Asia/Manila",
            "malaysia": "Asia/Kuala_Lumpur",
            "indonesia": "Asia/Jakarta"
        }
        
        if location:
            location = location.lower()
            timezone_str = timezone_map.get(location)
            
            if timezone_str:
                timezone = pytz.timezone(timezone_str)
                current_time = datetime.now(timezone)
                
                formatted_time = current_time.strftime("%I:%M %p")
                day = current_time.strftime("%A")
                
                response = f"It's {formatted_time} on {day} in {location.title()}"
                speak(response)
                return response
            else:
                response = f"Sorry, I don't have timezone information for {location}"
                speak(response)
                return response
        else:
            local_time = datetime.now()
            formatted_time = local_time.strftime("%I:%M %p")
            day = local_time.strftime("%A")
            
            response = f"The current local time is {formatted_time} on {day}"
            speak(response)
            return response
            
    except Exception as e:
        response = "Sorry, there was an error getting the time information."
        speak(response)
        return response

def get_movie_recommendation():
    try:
        # Using TMDB API (free with registration)
        api_key = "e4da343c7af228ff487e9d701a4593d1"  # Get from https://www.themoviedb.org/documentation/api
        url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}&language=en-US&page=1"
        
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and data['results']:
            movie = random.choice(data['results'])
            title = movie['title']
            rating = movie['vote_average']
            year = movie['release_date'].split('-')[0]
            overview = movie['overview']
            
            return f"I recommend watching '{title}' ({year}). It has a rating of {rating}/10. Here's what it's about: {overview}"
        else:
            return get_movie_recommendation_backup()
    except:
        return get_movie_recommendation_backup()

def get_movie_recommendation_backup():
    try:
        # Scraping IMDb Top 250 as backup
        url = "https://www.imdb.com/chart/top/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        movies = soup.select('td.titleColumn')
        movie = random.choice(movies)
        title = movie.a.text
        year = movie.span.text.strip('()')
        
        return f"I recommend watching '{title}' ({year}). It's one of IMDb's top-rated movies!"
    except:
        return "Sorry, I'm having trouble getting movie recommendations right now."

def get_song_recommendation():
    try:
        # Using Last.fm API (free with registration)
        api_key = "YOUR_LASTFM_API_KEY"  # Get from https://www.last.fm/api
        url = f"http://ws.audioscrobbler.com/2.0/?method=chart.gettoptracks&api_key={api_key}&format=json"
        
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            track = random.choice(data['tracks']['track'])
            song = track['name']
            artist = track['artist']['name']
            
            return f"I recommend listening to '{song}' by {artist}!"
        else:
            return get_song_recommendation_backup()
    except:
        return get_song_recommendation_backup()

def get_song_recommendation_backup():
    try:
        # Scraping Billboard Hot 100 as backup
        url = "https://www.billboard.com/charts/hot-100/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        songs = soup.select('h3.c-title')
        song = random.choice(songs[:20])  # Top 20 songs
        
        return f"I recommend listening to '{song.text.strip()}'! It's currently trending on Billboard!"
    except:
        return "Sorry, I'm having trouble getting song recommendations right now."

def get_book_recommendation():
    try:
        # Using Open Library API (free)
        subjects = ['love', 'science_fiction', 'fantasy', 'thriller', 'mystery', 'romance']
        subject = random.choice(subjects)
        url = f"https://openlibrary.org/subjects/{subject}.json"
        
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and data['works']:
            book = random.choice(data['works'])
            title = book['title']
            author = book['authors'][0]['name'] if book.get('authors') else "Unknown Author"
            
            return f"I recommend reading '{title}' by {author}!"
        else:
            return get_book_recommendation_backup()
    except:
        return get_book_recommendation_backup()

def get_book_recommendation_backup():
    try:
        # Scraping Goodreads as backup
        url = "https://www.goodreads.com/list/show/1.Best_Books_Ever"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        books = soup.select('a.bookTitle')
        book = random.choice(books[:50])  # Top 50 books
        
        return f"I recommend reading '{book.text.strip()}'! It's highly rated on Goodreads!"
    except:
        return "Sorry, I'm having trouble getting book recommendations right now."

def get_financial_tip():
    financial_tips = {
        "budgeting": [
            "Follow the 50/30/20 rule: 50% for needs, 30% for wants, and 20% for savings and debt repayment.",
            "Track your expenses for a month to understand your spending patterns.",
            "Create an emergency fund with 3-6 months of living expenses.",
            "Use cash instead of cards for discretionary spending to better control your budget.",
            "Review and cancel unused subscriptions and memberships."
        ],
        "saving": [
            "Automate your savings by setting up automatic transfers to your savings account.",
            "Save your tax refunds and any unexpected windfalls.",
            "Consider using high-yield savings accounts for better interest rates.",
            "Look for ways to reduce your utility bills through energy-efficient practices.",
            "Compare prices and use coupons for regular purchases."
        ],
        "investing": [
            "Start investing early to take advantage of compound interest.",
            "Diversify your investments across different asset classes.",
            "Consider low-cost index funds for long-term investing.",
            "Research before investing and never invest money you can't afford to lose.",
            "Regular small investments can be better than waiting to invest a large sum."
        ],
        "debt_management": [
            "Pay off high-interest debt first while maintaining minimum payments on other debts.",
            "Consider debt consolidation for multiple high-interest debts.",
            "Avoid taking on unnecessary debt for non-essential purchases.",
            "Build your credit score by paying bills on time and keeping credit utilization low.",
            "Consider balance transfer options for credit card debt."
        ]
    }
    
    category = random.choice(list(financial_tips.keys()))
    tip = random.choice(financial_tips[category])
    return f"Here's a tip about {category.replace('_', ' ')}: {tip}"

def get_stock_price(stock_symbol):
    try:
        stock = yf.Ticker(stock_symbol)
        info = stock.info
        
        current_price = info.get('currentPrice', 0)
        previous_close = info.get('previousClose', 0)
        company_name = info.get('longName', stock_symbol)
        
        # Calculate price change
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100
        
        return f"{company_name} ({stock_symbol}) is currently trading at ${current_price:.2f}. " \
               f"This is a {change_percent:.2f}% {'increase' if change >= 0 else 'decrease'} from the previous close."
    except:
        return f"Sorry, I couldn't fetch the stock information for {stock_symbol}."

def extract_stock_symbol(query):
    # Common stock market terms to remove
    stock_terms = ["stock", "price", "of", "check", "value", "market", "share", "shares", "trading", "at"]
    words = query.upper().split()
    # Remove common terms and return the likely stock symbol
    symbols = [word for word in words if word not in [term.upper() for term in stock_terms]]
    return symbols[-1] if symbols else None

def get_crypto_price(crypto_symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_symbol.lower()}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()
        
        if crypto_symbol.lower() in data:
            price = data[crypto_symbol.lower()]['usd']
            return f"The current price of {crypto_symbol.upper()} is ${price:,.2f}"
        else:
            return f"Sorry, I couldn't find price information for {crypto_symbol}"
    except:
        return "Sorry, I'm having trouble accessing cryptocurrency prices right now."

def get_market_summary():
    try:
        # Get major index data
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ'
        }
        
        summary = "Here's today's market summary:\n"
        
        for symbol, name in indices.items():
            index = yf.Ticker(symbol)
            info = index.info
            current = info.get('regularMarketPrice', 0)
            change = info.get('regularMarketChange', 0)
            change_percent = info.get('regularMarketChangePercent', 0)
            
            summary += f"{name}: {current:,.2f} ({change_percent:+.2f}%)\n"
        
        return summary
    except:
        return "Sorry, I'm having trouble accessing market data right now."

def get_game_recommendation():
    try:
        # Try RAWG API first (free with registration)
        api_key = "6839c488ce634ddca949ae326aa978f6"  # Get from https://rawg.io/apidocs
        current_year = datetime.now().year
        url = f"https://api.rawg.io/api/games?key={api_key}&dates={current_year-1},{current_year}&ordering=-rating&page_size=40"
        
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and data['results']:
            game = random.choice(data['results'])
            title = game['name']
            rating = game['rating']
            platforms = ", ".join([p['platform']['name'] for p in game['platforms'][:3]])
            genres = ", ".join([g['name'] for g in game['genres'][:3]])
            
            return f"I recommend playing '{title}'! It has a rating of {rating:.1f}/5. " \
                   f"Available on: {platforms}. Genres: {genres}"
        else:
            return get_game_recommendation_backup()
    except:
        return get_game_recommendation_backup()

def get_game_recommendation_backup():
    try:
        # Scrape Steam top games as backup
        url = "https://store.steampowered.com/search/?filter=topsellers"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        games = soup.select('div#search_resultsRows a')
        game = random.choice(games[:30])  # Top 30 games
        
        title = game.select_one('span.title').text
        price = game.select_one('div.search_price').text.strip()
        tags = game.select('div.search_tags span')
        genres = ", ".join([tag.text for tag in tags[:3]])
        
        return f"I recommend checking out '{title}' on Steam! Genres: {genres}"
    except:
        return get_free_games_recommendation()

def get_free_games_recommendation():
    free_games = {
        "Action": [
            "Fortnite - A popular battle royale game with building mechanics",
            "Apex Legends - A fast-paced battle royale with unique heroes",
            "Destiny 2 - A sci-fi MMO shooter with great graphics and gameplay",
            "Warframe - A fast-paced sci-fi action game with ninja-like gameplay"
        ],
        "RPG": [
            "Genshin Impact - An open-world action RPG with anime styling",
            "Path of Exile - A complex action RPG similar to Diablo",
            "Lost Ark - A top-down MMO action RPG with great combat",
            "Star Wars: The Old Republic - A story-rich MMO RPG"
        ],
        "Strategy": [
            "League of Legends - A popular MOBA with strategic team gameplay",
            "Dota 2 - A complex MOBA with deep strategic elements",
            "Hearthstone - A digital card game with strategic deck building",
            "StarCraft II - A classic RTS game with great multiplayer"
        ],
        "Casual": [
            "Rocket League - Soccer with cars, now free-to-play",
            "Fall Guys - A fun battle royale party game",
            "Brawlhalla - A platform fighter similar to Super Smash Bros",
            "Team Fortress 2 - A classic team-based shooter with unique characters"
        ]
    }
    
    genre = random.choice(list(free_games.keys()))
    game = random.choice(free_games[genre])
    return f"Here's a free {genre} game recommendation: {game}"

def get_mobile_game_recommendation():
    mobile_games = {
        "Casual": [
            "Among Us - A social deduction game that's fun with friends",
            "Pokemon GO - An AR game about catching Pokemon in the real world",
            "Candy Crush - A classic match-3 puzzle game",
            "Temple Run - An endless runner with simple controls"
        ],
        "Strategy": [
            "Clash Royale - A real-time strategy card game",
            "Auto Chess - A strategic auto-battler game",
            "Plants vs. Zombies - A fun tower defense game",
            "Rise of Kingdoms - A civilization building strategy game"
        ],
        "RPG": [
            "Raid: Shadow Legends - A turn-based RPG with collectible heroes",
            "AFK Arena - An idle RPG with strategic team building",
            "Final Fantasy Brave Exvius - A classic JRPG experience",
            "Dragon Ball Legends - An action RPG with famous anime characters"
        ],
        "Action": [
            "PUBG Mobile - A battle royale game on mobile",
            "Call of Duty Mobile - A first-person shooter with multiple modes",
            "Brawl Stars - A fast-paced multiplayer action game",
            "Shadow Fight 3 - A fighting game with RPG elements"
        ]
    }
    
    genre = random.choice(list(mobile_games.keys()))
    game = random.choice(mobile_games[genre])
    return f"Here's a mobile {genre} game recommendation: {game}"

def get_career_advice():
    career_tips = {
        "job_search": [
            {
                "tip": "Optimize your LinkedIn profile with relevant keywords and a professional photo",
                "details": "Make sure your profile is complete, includes your achievements, and uses industry-specific keywords."
            },
            {
                "tip": "Set up job alerts on multiple platforms",
                "details": "Use LinkedIn, Indeed, Glassdoor, and industry-specific job boards to maximize your opportunities."
            },
            {
                "tip": "Network actively in your industry",
                "details": "Attend industry events, join professional groups, and engage with professionals in your field."
            }
        ],
        "resume": [
            {
                "tip": "Tailor your resume for each job application",
                "details": "Match your skills and experiences to the job requirements and use relevant keywords from the job posting."
            },
            {
                "tip": "Quantify your achievements",
                "details": "Use numbers and percentages to demonstrate your impact, like 'Increased sales by 25%' or 'Managed a team of 12'."
            },
            {
                "tip": "Keep your resume concise and well-formatted",
                "details": "Limit it to 1-2 pages, use clear headings, and ensure consistent formatting throughout."
            }
        ],
        "interview": [
            {
                "tip": "Research the company thoroughly before interviews",
                "details": "Study their products/services, recent news, company culture, and prepare questions to ask."
            },
            {
                "tip": "Use the STAR method for behavioral questions",
                "details": "Structure your answers with Situation, Task, Action, and Result to provide clear, compelling examples."
            },
            {
                "tip": "Practice common interview questions",
                "details": "Prepare answers for questions about your experience, strengths, weaknesses, and career goals."
            }
        ],
        "career_development": [
            {
                "tip": "Keep learning and updating your skills",
                "details": "Take online courses, get certifications, and stay current with industry trends."
            },
            {
                "tip": "Find a mentor in your field",
                "details": "A mentor can provide guidance, share experiences, and help you navigate career challenges."
            },
            {
                "tip": "Set clear career goals",
                "details": "Define short-term and long-term career objectives, and create action plans to achieve them."
            }
        ],
        "career_change": [
            {
                "tip": "Identify transferable skills",
                "details": "Focus on skills that apply across industries like leadership, communication, and problem-solving."
            },
            {
                "tip": "Start with side projects",
                "details": "Build experience in your target field through freelance work, volunteering, or personal projects."
            },
            {
                "tip": "Network in your target industry",
                "details": "Connect with professionals in your desired field and learn from their experiences."
            }
        ]
    }

    # Randomly select a category and tip
    category = random.choice(list(career_tips.keys()))
    tip_data = random.choice(career_tips[category])
    
    category_name = category.replace('_', ' ').title()
    return f"Here's some advice about {category_name}:\n\n" \
           f"Tip: {tip_data['tip']}\n\n" \
           f"Details: {tip_data['details']}"

def get_job_market_trends():
    growing_fields = {
        "Technology": [
            "Artificial Intelligence and Machine Learning",
            "Cybersecurity",
            "Cloud Computing",
            "Data Science",
            "DevOps"
        ],
        "Healthcare": [
            "Telemedicine",
            "Mental Health Services",
            "Healthcare Information Technology",
            "Biotechnology",
            "Remote Patient Monitoring"
        ],
        "Remote Work": [
            "Digital Project Management",
            "Virtual Team Leadership",
            "Remote Customer Service",
            "Online Teaching",
            "Digital Marketing"
        ],
        "Sustainability": [
            "Renewable Energy",
            "Environmental Conservation",
            "Sustainable Business Practices",
            "Green Technology",
            "Climate Change Mitigation"
        ]
    }

    field = random.choice(list(growing_fields.keys()))
    trends = growing_fields[field]
    
    response = f"Here are some growing opportunities in {field}:\n"
    for trend in trends:
        response += f"- {trend}\n"
    
    return response

def get_skill_development_advice():
    skills_advice = {
        "Technical Skills": [
            "Learn programming languages like Python or JavaScript",
            "Get certified in cloud platforms (AWS, Azure, GCP)",
            "Study data analysis and visualization tools",
            "Learn about cybersecurity fundamentals",
            "Understand basic web development"
        ],
        "Soft Skills": [
            "Practice public speaking and presentation skills",
            "Develop emotional intelligence and empathy",
            "Improve written and verbal communication",
            "Learn conflict resolution techniques",
            "Build leadership and team management abilities"
        ],
        "Digital Skills": [
            "Master digital collaboration tools",
            "Learn social media management",
            "Understand basic SEO principles",
            "Practice digital content creation",
            "Learn about digital marketing basics"
        ]
    }

    category = random.choice(list(skills_advice.keys()))
    skill = random.choice(skills_advice[category])
    
    return f"Here's a skill development suggestion for {category}:\n{skill}"

def get_greeting():
    current_hour = datetime.now().hour
    
    if current_hour < 12:
        return "Good morning!"
    elif current_hour < 17:
        return "Good afternoon!"
    else:
        return "Good evening!"

def initial_greeting():
    greeting = get_greeting()
    speak(f"{greeting} I am Parzefal, your AI assistant. How may I help you today?")


initial_greeting()
while True:
    user_input = speechrecognition()
    if user_input.lower() == "exit":
        print("AI Assistant Bye!")
        break
    
    intent = predict_intent(user_input)
    if intent == "weather":
        city = extract_city(user_input)
        if city:
            weather_info = get_weather(city)
            speak(weather_info)
        else:
            speak("Please specify a city name for the weather information.")
    elif intent == "time":
        if "in" in user_input.lower():
            location = extract_location(user_input)
            if location:
                get_time(location)
            else:
                speak("Please specify a location for the time check.")
        else:
            # Get local time
            get_time()
    elif intent == "movie_recommendation":
        recommendation = get_movie_recommendation()
        speak(recommendation)
    elif intent == "song_recommendation":
        recommendation = get_song_recommendation()
        speak(recommendation)
    elif intent == "book_recommendation":
        recommendation = get_book_recommendation()
        speak(recommendation)
    elif intent == "finance_advice":
        advice = get_financial_tip()
        speak(advice)
    elif intent == "stock_price":
        symbol = extract_stock_symbol(user_input)
        if symbol:
            price_info = get_stock_price(symbol)
            speak(price_info)
        else:
            speak("Please specify a stock symbol. For example, 'Check stock price of AAPL'")
    elif "crypto" in user_input.lower():
        symbol = extract_stock_symbol(user_input)
        if symbol:
            crypto_info = get_crypto_price(symbol)
            speak(crypto_info)
        else:
            speak("Please specify a cryptocurrency symbol. For example, 'Check crypto price of BTC'")
    elif "market summary" in user_input.lower():
        summary = get_market_summary()
        speak(summary)
    elif intent in intents:
        responses = intents[intent]['responses']
        response = random.choice(responses)
        speak(response)
    elif intent == "game_recommendation":
        if "mobile" in user_input.lower():
            recommendation = get_mobile_game_recommendation()
        elif "free" in user_input.lower():
            recommendation = get_free_games_recommendation()
        else:
            recommendation = get_game_recommendation()
        speak(recommendation)
    else:
        speak("I'm not sure how to answer to that")
    
    
            