# add_dummy_data.py
# FULL REALISTIC DATA – 20 MATCHES – NO ZERO SCORES – ELITE BIAS

import requests
import random
import time
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:5000/api"
HEADERS = {"Content-Type": "application/json"}


TEAMS = {
    "India": [
        ("Rohit Sharma", "batsman"), ("Virat Kohli", "batsman"), ("Jasprit Bumrah", "bowler"),
        ("Ravindra Jadeja", "all-rounder"), ("Mohammed Siraj", "bowler"), ("KL Rahul", "wicket-keeper"),
        ("Shubman Gill", "batsman"), ("Mohammed Shami", "bowler"), ("Rishabh Pant", "wicket-keeper"),
        ("Kuldeep Yadav", "bowler"), ("Axar Patel", "all-rounder"), ("Yashasvi Jaiswal", "batsman"),
        ("Shreyas Iyer", "batsman"), ("Washington Sundar", "all-rounder"), ("Mukesh Kumar", "bowler"),
        ("Arshdeep Singh", "bowler"), ("Prasidh Krishna", "bowler"), ("Rajat Patidar", "batsman"),
        ("Dhruv Jurel", "wicket-keeper"), ("Sarfaraz Khan", "batsman"), ("Nitish Kumar Reddy", "all-rounder"),
        ("Ishan Kishan", "wicket-keeper"), ("Akash Deep", "bowler"), ("Harshit Rana", "bowler"),
        ("Abhimanyu Easwaran", "batsman"), ("KS Bharat", "wicket-keeper"), ("Navdeep Saini", "bowler"),
        ("Saurabh Kumar", "bowler"), ("Jayant Yadav", "all-rounder"), ("Devdutt Padikkal", "batsman")
    ],
    "Australia": [
        ("Pat Cummins", "bowler"), ("Steve Smith", "batsman"), ("Marnus Labuschagne", "batsman"),
        ("Travis Head", "batsman"), ("Usman Khawaja", "batsman"), ("Mitchell Starc", "bowler"),
        ("Josh Hazlewood", "bowler"), ("Nathan Lyon", "bowler"), ("Alex Carey", "wicket-keeper"),
        ("Cameron Green", "all-rounder"), ("Mitchell Marsh", "all-rounder"), ("Scott Boland", "bowler"),
        ("Todd Murphy", "bowler"), ("Marcus Harris", "batsman"), ("Peter Handscomb", "batsman"),
        ("Michael Neser", "all-rounder"), ("Jhye Richardson", "bowler"), ("Lance Morris", "bowler"),
        ("Beau Webster", "all-rounder"), ("Matt Renshaw", "batsman"), ("Josh Inglis", "wicket-keeper"),
        ("Sean Abbott", "all-rounder"), ("Aaron Hardie", "all-rounder"), ("Caleb Jewell", "batsman"),
        ("Will Pucovski", "batsman"), ("Ashton Agar", "all-rounder"), ("Adam Zampa", "bowler"),
        ("Riley Meredith", "bowler"), ("Matt Kuhnemann", "bowler"), ("Daniel Sams", "all-rounder")
    ],
    "England": [
        ("Joe Root", "batsman"), ("Ben Stokes", "all-rounder"), ("Ollie Pope", "batsman"),
        ("Zak Crawley", "batsman"), ("Ben Duckett", "batsman"), ("Harry Brook", "batsman"),
        ("Jonny Bairstow", "wicket-keeper"), ("Chris Woakes", "all-rounder"), ("Mark Wood", "bowler"),
        ("Ollie Robinson", "bowler"), ("Rehan Ahmed", "bowler"), ("Jack Leach", "bowler"),
        ("Gus Atkinson", "bowler"), ("James Anderson", "bowler"), ("Tom Hartley", "bowler"),
        ("Shoaib Bashir", "bowler"), ("Matthew Potts", "bowler"), ("Sam Curran", "all-rounder"),
        ("Ollie Lawrence", "batsman"), ("Dan Lawrence", "batsman"), ("Ben Foakes", "wicket-keeper"),
        ("Josh Tongue", "bowler"), ("Jamie Overton", "all-rounder"), ("Craig Overton", "all-rounder"),
        ("Dawid Malan", "batsman"), ("Liam Livingstone", "all-rounder"), ("Brydon Carse", "bowler"),
        ("Zak Chappell", "bowler"), ("Will Jacks", "all-rounder"), ("George Balderson", "all-rounder")
    ],
    "South Africa": [
        ("Temba Bavuma", "batsman"), ("Aiden Markram", "batsman"), ("Kagiso Rabada", "bowler"),
        ("Anrich Nortje", "bowler"), ("Marco Jansen", "all-rounder"), ("Keshav Maharaj", "bowler"),
        ("Lungi Ngidi", "bowler"), ("David Bedingham", "batsman"), ("Tony de Zorzi", "batsman"),
        ("Kyle Verreynne", "wicket-keeper"), ("Gerald Coetzee", "bowler"), ("Wiaan Mulder", "all-rounder"),
        ("Keegan Petersen", "batsman"), ("Zubayr Hamza", "batsman"), ("Ryan Rickelton", "wicket-keeper"),
        ("Tristan Stubbs", "batsman"), ("Senuran Muthusamy", "all-rounder"), ("Dane Paterson", "bowler"),
        ("Andile Phehlukwayo", "all-rounder"), ("Tabraiz Shamsi", "bowler"), ("Bjorn Fortuin", "bowler"),
        ("Sisanda Magala", "bowler"), ("Nandre Burger", "bowler"), ("Corbin Bosch", "all-rounder"),
        ("Matthew Breetzke", "batsman"), ("Ruan de Swardt", "all-rounder"), ("Lizaad Williams", "bowler"),
        ("George Linde", "all-rounder"), ("Prenelan Subrayen", "bowler"), ("Grant Roelofsen", "wicket-keeper")
    ],
    "New Zealand": [
        ("Kane Williamson", "batsman"), ("Tim Southee", "bowler"), ("Tom Latham", "batsman"),
        ("Devon Conway", "batsman"), ("Daryl Mitchell", "all-rounder"), ("Tom Blundell", "wicket-keeper"),
        ("Will Young", "batsman"), ("Ajaz Patel", "bowler"), ("Mitchell Santner", "all-rounder"),
        ("Kyle Jamieson", "bowler"), ("Neil Wagner", "bowler"), ("Matt Henry", "bowler"),
        ("Rachin Ravindra", "all-rounder"), ("Glenn Phillips", "batsman"), ("Henry Nicholls", "batsman"),
        ("Ish Sodhi", "bowler"), ("Will O’Rourke", "bowler"), ("Ben Sears", "bowler"),
        ("Jacob Duffy", "bowler"), ("Adam Milne", "bowler"), ("Scott Kuggeleijn", "all-rounder"),
        ("Mark Chapman", "batsman"), ("Finn Allen", "batsman"), ("Dane Cleaver", "wicket-keeper"),
        ("Michael Bracewell", "all-rounder"), ("Zak Foulkes", "bowler"), ("Doug Bracewell", "all-rounder"),
        ("Sean Solia", "all-rounder"), ("Cole McConchie", "all-rounder"), ("Tim Seifert", "wicket-keeper")
    ],
    "Pakistan": [
        ("Babar Azam", "batsman"), ("Mohammad Rizwan", "wicket-keeper"), ("Shan Masood", "batsman"),
        ("Abdullah Shafique", "batsman"), ("Saud Shakeel", "batsman"), ("Imam-ul-Haq", "batsman"),
        ("Shaheen Afridi", "bowler"), ("Naseem Shah", "bowler"), ("Abrar Ahmed", "bowler"),
        ("Agha Salman", "all-rounder"), ("Sarfaraz Ahmed", "wicket-keeper"), ("Faheem Ashraf", "all-rounder"),
        ("Hasan Ali", "bowler"), ("Khurram Shahzad", "bowler"), ("Mir Hamza", "bowler"),
        ("Mohammad Wasim Jr", "bowler"), ("Nauman Ali", "bowler"), ("Zahid Mahmood", "bowler"),
        ("Saud Khan", "batsman"), ("Saim Ayub", "batsman"), ("Azam Khan", "wicket-keeper"),
        ("Shanawaz Dahani", "bowler"), ("Usama Mir", "bowler"), ("Haris Rauf", "bowler"),
        ("Shadab Khan", "all-rounder"), ("Iftikhar Ahmed", "all-rounder"), ("Kamran Ghulam", "batsman"),
        ("Mohammad Ali", "bowler"), ("Zaman Khan", "bowler"), ("Arshad Iqbal", "bowler")
    ],
    "Sri Lanka": [
        ("Dimuth Karunaratne", "batsman"), ("Angelo Mathews", "all-rounder"), ("Dinesh Chandimal", "batsman"),
        ("Kusal Mendis", "wicket-keeper"), ("Pathum Nissanka", "batsman"), ("Prabath Jayasuriya", "bowler"),
        ("Kasun Rajitha", "bowler"), ("Lahiru Kumara", "bowler"), ("Ramesh Mendis", "all-rounder"),
        ("Dhananjaya de Silva", "all-rounder"), ("Sadeera Samarawickrama", "wicket-keeper"),
        ("Oshada Fernando", "batsman"), ("Nishan Madushka", "batsman"), ("Kamindu Mendis", "all-rounder"),
        ("Wanindu Hasaranga", "all-rounder"), ("Maheesh Theekshana", "bowler"), ("Jeffrey Vandersay", "bowler"),
        ("Asitha Fernando", "bowler"), ("Vishwa Fernando", "bowler"), ("Chamika Karunaratne", "all-rounder"),
        ("Dunith Wellalage", "all-rounder"), ("Lahiru Udara", "wicket-keeper"), ("Milan Rathnayake", "bowler"),
        ("Nuwan Thushara", "bowler"), ("Binura Fernando", "bowler"), ("Avishka Fernando", "batsman"),
        ("Charith Asalanka", "batsman"), ("Minod Bhanuka", "wicket-keeper"), ("Ashen Bandara", "batsman"),
        ("Pathum Kumara", "bowler")
    ],
    "Bangladesh": [
        ("Shakib Al Hasan", "all-rounder"), ("Mushfiqur Rahim", "wicket-keeper"), ("Litton Das", "wicket-keeper"),
        ("Najmul Hossain Shanto", "batsman"), ("Mehidy Hasan Miraz", "all-rounder"), ("Taskin Ahmed", "bowler"),
        ("Mustafizur Rahman", "bowler"), ("Taijul Islam", "bowler"), ("Ebadot Hossain", "bowler"),
        ("Hasan Mahmud", "bowler"), ("Shoriful Islam", "bowler"), ("Zakir Hasan", "batsman"),
        ("Mahmudul Hasan Joy", "batsman"), ("Mominul Haque", "batsman"), ("Nurul Hasan", "wicket-keeper"),
        ("Soumya Sarkar", "batsman"), ("Nasum Ahmed", "bowler"), ("Mosaddek Hossain", "all-rounder"),
        ("Yasir Ali", "batsman"), ("Khaled Ahmed", "bowler"), ("Taijul Islam Jr", "bowler"),
        ("Rony Talukdar", "batsman"), ("Anamul Haque", "wicket-keeper"), ("Afif Hossain", "batsman"),
        ("Tanzid Hasan", "batsman"), ("Nayeem Hasan", "bowler"), ("Rejaur Rahman Raja", "bowler"),
        ("Tanzim Hasan Sakib", "bowler"), ("Ripon Mondol", "bowler"), ("Shuvagata Hom", "all-rounder")
    ],
    "West Indies": [
        ("Kraigg Brathwaite", "batsman"), ("Jason Holder", "all-rounder"), ("Alzarri Joseph", "bowler"),
        ("Kemar Roach", "bowler"), ("Kyle Mayers", "all-rounder"), ("Joshua Da Silva", "wicket-keeper"),
        ("Gudakesh Motie", "bowler"), ("Shamar Joseph", "bowler"), ("Alick Athanaze", "batsman"),
        ("Tagenarine Chanderpaul", "batsman"), ("Justin Greaves", "batsman"), ("Roston Chase", "all-rounder"),
        ("Keacy Carty", "batsman"), ("Jermaine Blackwood", "batsman"), ("Oshane Thomas", "bowler"),
        ("Jayden Seales", "bowler"), ("Romario Shepherd", "all-rounder"), ("Yannic Cariah", "bowler"),
        ("Jomel Warrican", "bowler"), ("Shannon Gabriel", "bowler"), ("Nkrumah Bonner", "batsman"),
        ("Devon Thomas", "wicket-keeper"), ("Odean Smith", "all-rounder"), ("Fabian Allen", "all-rounder"),
        ("Sherfane Rutherford", "batsman"), ("Rahkeem Cornwall", "all-rounder"), ("Johnson Charles", "batsman"),
        ("Hayden Walsh", "bowler"), ("Preston McSween", "bowler"), ("Jeremy Solozano", "batsman")
    ],
    "Zimbabwe": [
        ("Craig Ervine", "batsman"), ("Sean Williams", "all-rounder"), ("Sikandar Raza", "all-rounder"),
        ("Blessing Muzarabani", "bowler"), ("Richard Ngarava", "bowler"), ("Tendai Chatara", "bowler"),
        ("Joylord Gumbie", "wicket-keeper"), ("Wellington Masakadza", "bowler"), ("Ryan Burl", "batsman"),
        ("Luke Jongwe", "all-rounder"), ("Innocent Kaia", "batsman"), ("Wessly Madhevere", "all-rounder"),
        ("Milton Shumba", "batsman"), ("Victor Nyauchi", "bowler"), ("Tanaka Chivanga", "bowler"),
        ("Prince Masvaure", "batsman"), ("Takudzwanashe Kaitano", "batsman"), ("Tadiwanashe Marumani", "batsman"),
        ("Regis Chakabva", "wicket-keeper"), ("Clive Madande", "wicket-keeper"), ("Brandon Mavuta", "bowler"),
        ("Donald Tiripano", "all-rounder"), ("Faraz Akram", "bowler"), ("Tony Munyonga", "batsman"),
        ("Newman Nyamhuri", "bowler"), ("Tafadzwa Tsiga", "wicket-keeper"), ("Richard Mutumbami", "wicket-keeper"),
        ("Ainsley Ndlovu", "bowler"), ("Blessing Mudzinganyama", "batsman"), ("Kudakwashe Mupfudza", "batsman")
    ],
    "Afghanistan": [
        ("Rashid Khan", "bowler"), ("Rahmat Shah", "batsman"), ("Hashmatullah Shahidi", "batsman"),
        ("Ibrahim Zadran", "batsman"), ("Mujeeb Ur Rahman", "bowler"), ("Naveen-ul-Haq", "bowler"),
        ("Noor Ahmad", "bowler"), ("Ikram Alikhil", "wicket-keeper"), ("Rahmanullah Gurbaz", "wicket-keeper"),
        ("Azmatullah Omarzai", "all-rounder"), ("Mohammad Nabi", "all-rounder"), ("Zia-ur-Rahman", "bowler"),
        ("Najibullah Zadran", "batsman"), ("Fareed Ahmad", "bowler"), ("Qais Ahmad", "bowler"),
        ("Karim Janat", "all-rounder"), ("Gulbadin Naib", "all-rounder"), ("Darwish Rasooli", "batsman"),
        ("Sharafuddin Ashraf", "all-rounder"), ("Yamin Ahmadzai", "bowler"), ("Wafadar Momand", "bowler"),
        ("Fazalhaq Farooqi", "bowler"), ("Naveed Zadran", "bowler"), ("Shapoor Zadran", "bowler"),
        ("Bahir Shah", "batsman"), ("Afsar Zazai", "wicket-keeper"), ("Ihsanullah Janat", "batsman"),
        ("Riaz Hassan", "batsman"), ("Samiullah Shinwari", "all-rounder"), ("Sayed Shirzad", "bowler")
    ],
    "Ireland": [
        ("Andy Balbirnie", "batsman"), ("Paul Stirling", "batsman"), ("Curtis Campher", "all-rounder"),
        ("Mark Adair", "all-rounder"), ("George Dockrell", "all-rounder"), ("Harry Tector", "batsman"),
        ("Lorcan Tucker", "wicket-keeper"), ("Andrew McBrine", "all-rounder"), ("Barry McCarthy", "bowler"),
        ("Josh Little", "bowler"), ("Craig Young", "bowler"), ("Matthew Humphreys", "bowler"),
        ("Ben White", "bowler"), ("Fionn Hand", "bowler"), ("Stephen Doheny", "wicket-keeper"),
        ("Murray Commins", "batsman"), ("Neil Rock", "wicket-keeper"), ("Gareth Delany", "all-rounder"),
        ("Andy McBrine Jr", "all-rounder"), ("William Porterfield", "batsman"), ("Tim Tector", "batsman"),
        ("Theo van Woerkom", "bowler"), ("Ross Adair", "batsman"), ("Peter Moor", "wicket-keeper"),
        ("Shane Getkate", "all-rounder"), ("Max Sorensen", "bowler"), ("Boyd Rankin", "bowler"),
        ("Simi Singh", "all-rounder"), ("Kevin O’Brien", "all-rounder"), ("Mark Donegan", "wicket-keeper")
    ],
    "Scotland": [
        ("Richie Berrington", "batsman"), ("George Munsey", "batsman"), ("Matthew Cross", "wicket-keeper"),
        ("Michael Leask", "all-rounder"), ("Mark Watt", "bowler"), ("Safyaan Sharif", "bowler"),
        ("Chris Sole", "bowler"), ("Brad Wheal", "bowler"), ("Brandon McMullen", "all-rounder"),
        ("Calum MacLeod", "batsman"), ("Kyle Coetzer", "batsman"), ("Oli Hairs", "batsman"),
        ("Chris Greaves", "all-rounder"), ("Tom Mackintosh", "wicket-keeper"), ("Hamza Tahir", "bowler"),
        ("Alasdair Evans", "bowler"), ("Michael Jones", "batsman"), ("Charlie Tear", "wicket-keeper"),
        ("Finlay McCreath", "bowler"), ("Jasper Davidson", "bowler"), ("Cameron Slater", "batsman"),
        ("Jack Jarvis", "all-rounder"), ("Andrew Umeed", "batsman"), ("Niall McBeth", "bowler"),
        ("Ben Davidson", "bowler"), ("Oliver Davidson", "all-rounder"), ("Conor McMullen", "batsman"),
        ("Theo Currie", "batsman"), ("Liam Naylor", "batsman"), ("Jayden Goodwin", "batsman")
    ],
    "Nepal": [
        ("Rohit Paudel", "batsman"), ("Dipendra Singh Airee", "all-rounder"), ("Sandeep Lamichhane", "bowler"),
        ("Sompal Kami", "bowler"), ("Karan KC", "bowler"), ("Aasif Sheikh", "wicket-keeper"),
        ("Kushal Bhurtel", "batsman"), ("Kushal Malla", "all-rounder"), ("Gyanendra Malla", "batsman"),
        ("Aarif Sheikh", "batsman"), ("Lalit Rajbanshi", "bowler"), ("Pratis GC", "bowler"),
        ("Gulshan Jha", "bowler"), ("Anil Sah", "wicket-keeper"), ("Bibek Yadav", "bowler"),
        ("Kamal Singh Airee", "bowler"), ("Sagar Dhakal", "bowler"), ("Pawan Sarraf", "all-rounder"),
        ("Ishan Pandey", "bowler"), ("Dev Khanal", "batsman"), ("Basir Ahamad", "bowler"),
        ("Surya Tamang", "bowler"), ("Rijan Dhakal", "bowler"), ("Mahesh Tamang", "batsman"),
        ("Abhinash Bohara", "bowler"), ("Narayan Joshi", "bowler"), ("Sandeep Jora", "batsman"),
        ("Rohit Kumar Paudel Jr", "batsman"), ("Dipak Bohara", "bowler"), ("Hemanta Dhami", "bowler")
    ],
    "United Arab Emirates": [
        ("Muhammad Waseem", "batsman"), ("Vriitya Aravind", "wicket-keeper"), ("Chirag Suri", "batsman"),
        ("Rohan Mustafa", "all-rounder"), ("Basil Hameed", "all-rounder"), ("Alishan Sharafu", "batsman"),
        ("Asif Khan", "batsman"), ("Aryansh Sharma", "wicket-keeper"), ("Zahoor Khan", "bowler"),
        ("Junaid Siddique", "bowler"), ("Aayan Khan", "all-rounder"), ("Karthik Meiyappan", "bowler"),
        ("Akif Raja", "bowler"), ("Sabir Ali", "bowler"), ("Nilansh Keswani", "all-rounder"),
        ("Mohammad Zahid", "bowler"), ("Kashif Daud", "all-rounder"), ("Zawar Farid", "all-rounder"),
        ("Waseem Muhammad", "batsman"), ("Rahul Chopra", "batsman"), ("Fahad Nawaz", "batsman"),
        ("Mohammad Jawadullah", "bowler"), ("Ethan D’Souza", "batsman"), ("Matiullah Khan", "bowler"),
        ("Umair Ali", "all-rounder"), ("Sultan Ahmed", "bowler"), ("Muhammad Farazuddin", "bowler"),
        ("Rameez Shahzad", "batsman"), ("Shahid Afridi Jr", "bowler"), ("Sanchit Sharma", "bowler")
    ],
    "Oman": [
        ("Zeeshan Maqsood", "all-rounder"), ("Aqib Ilyas", "all-rounder"), ("Jatinder Singh", "batsman"),
        ("Kashyap Prajapati", "batsman"), ("Ayaan Khan", "all-rounder"), ("Mohammad Nadeem", "all-rounder"),
        ("Fayyaz Butt", "bowler"), ("Bilal Khan", "bowler"), ("Kaleemullah", "bowler"),
        ("Sandeep Goud", "batsman"), ("Shoaib Khan", "batsman"), ("Suraj Kumar", "wicket-keeper"),
        ("Naseem Khushi", "wicket-keeper"), ("Mehran Khan", "all-rounder"), ("Pratik Athavale", "wicket-keeper"),
        ("Jay Odedra", "bowler"), ("Muzahir Raza", "bowler"), ("Aamir Kaleem", "all-rounder"),
        ("Shakeel Ahmad", "bowler"), ("Siddharth Bukkapatnam", "bowler"), ("Rafiullah", "batsman"),
        ("Samay Shrivastava", "bowler"), ("Wasim Ali", "all-rounder"), ("Kiran Sonavane", "batsman"),
        ("Darsan Tandel", "bowler"), ("Yousuf Ali", "bowler"), ("Arjun Lalcheta", "all-rounder"),
        ("Afzal Khan", "bowler"), ("Rahul Gopal", "batsman"), ("Vinayak Shukla", "wicket-keeper")
    ],
    "United States of America": [
        ("Monank Patel", "wicket-keeper"), ("Steven Taylor", "batsman"), ("Aaron Jones", "batsman"),
        ("Nitish Kumar", "batsman"), ("Ali Khan", "bowler"), ("Saurabh Netravalkar", "bowler"),
        ("Corey Anderson", "all-rounder"), ("Shayan Jahangir", "batsman"), ("Andries Gous", "wicket-keeper"),
        ("Jessy Singh", "bowler"), ("Nosthush Kenjige", "bowler"), ("Harmeet Singh", "all-rounder"),
        ("Milind Kumar", "batsman"), ("Gajanand Singh", "batsman"), ("Nisarg Patel", "all-rounder"),
        ("Shubham Ranjane", "all-rounder"), ("Saiteja Mukkamalla", "batsman"), ("Sanjay Krishnamurthi", "all-rounder"),
        ("Juanoy Drysdale", "bowler"), ("Utkarsh Srivastava", "bowler"), ("Cameron Stevenson", "bowler"),
        ("Yasir Mohammad", "bowler"), ("Rahul Jariwala", "wicket-keeper"), ("Ehsan Adil", "bowler"),
        ("Liam Plunkett", "bowler"), ("Smit Patel", "wicket-keeper"), ("Kenjige Jr", "bowler"),
        ("Abhishek Paradkar", "bowler"), ("Shehan Jayasuriya", "all-rounder"), ("Vatsal Vaghela", "bowler")
    ]
}


# ======================================================
# ELITE PLAYERS (REAL WORLD BIAS)
# ======================================================
ELITE_BATSMEN = {
    "Virat Kohli", "Rohit Sharma", "Babar Azam", "Steve Smith",
    "Joe Root", "Kane Williamson", "Shubman Gill",
    "Harry Brook", "Travis Head"
}

ELITE_BOWLERS = {
    "Jasprit Bumrah", "Shaheen Afridi", "Rashid Khan",
    "Pat Cummins", "Mitchell Starc", "Kagiso Rabada"
}

# ======================================================
# MATCH SCHEDULE – 20 MATCHES
# ======================================================
MATCHES = [
    ("India", "Australia"), ("England", "South Africa"),
    ("Pakistan", "New Zealand"), ("India", "England"),
    ("Australia", "South Africa"), ("Pakistan", "Sri Lanka"),
    ("India", "New Zealand"), ("Australia", "England"),
    ("South Africa", "West Indies"), ("India", "Pakistan"),
    ("Sri Lanka", "Bangladesh"), ("Afghanistan", "Ireland"),
    ("Scotland", "Nepal"), ("Zimbabwe", "West Indies"),
   ("United Arab Emirates", "Oman"),
("United States of America", "Ireland"),
    ("Bangladesh", "Pakistan"), ("South Africa", "India"),
    ("England", "Australia"), ("New Zealand", "Sri Lanka")
]

# ======================================================
# UTILITIES
# ======================================================
def safe_request(method, url, **kwargs):
    try:
        r = requests.request(method, url, timeout=10, **kwargs)
        return r if r.status_code in (200, 201) else None
    except:
        return None

def get_json(r):
    try:
        return r.json() if r else None
    except:
        return None

# ======================================================
# REALISTIC MATCH-BASED BATSMAN SCORE
# ======================================================
def batting_score(name, role):
    if name in ELITE_BATSMEN:
        return random.choices(
            [random.randint(50, 120), random.randint(25, 49), random.randint(10, 24)],
            [45, 35, 20]
        )[0]

    if role == "batsman":
        return random.randint(15, 85)
    if role == "wicket-keeper":
        return random.randint(12, 70)
    if role == "all-rounder":
        return random.randint(10, 60)

    return random.randint(3, 25)  # bowlers

# ======================================================
# REALISTIC MATCH-BASED BOWLING
# ======================================================
def bowling_figures(name, role):
    if role not in ["bowler", "all-rounder"]:
        return 0.0, 0, 0

    overs = round(random.uniform(1.0, 4.0), 1)

    if name in ELITE_BOWLERS:
        wickets = random.choices([1, 2, 3, 4], [30, 35, 25, 10])[0]
        economy = random.uniform(5.5, 7.5)
    else:
        wickets = random.choices([0, 1, 2, 3], [30, 40, 20, 10])[0]
        economy = random.uniform(6.5, 9.5)

    conceded = int(overs * economy)
    return overs, wickets, conceded

# ======================================================
# CREATE MATCHES + FULL PLAYER PERFORMANCE
# ======================================================
def create_matches(team_info, all_players):
    start_date = datetime.now() - timedelta(days=90)

    for i, (t1, t2) in enumerate(MATCHES, 1):
        r = safe_request("POST", f"{API_URL}/matches", json={
            "name": f"{t1} vs {t2} – T20 Match {i}",
            "date": (start_date + timedelta(days=i * 4)).strftime("%Y-%m-%d"),
            "team1_id": team_info[t1],
            "team2_id": team_info[t2]
        }, headers=HEADERS)

        match = get_json(r)
        if not match:
            continue

        match_id = match["match_id"]
        print(f"✔ Match {i}: {t1} vs {t2}")

        for team in [t1, t2]:
            squad = list(all_players[team].items())
            playing_xi = random.sample(squad, 11)

            for name, pid in squad:
                role = next(r for tm in TEAMS.values() for n, r in tm if n == name)

                # -------- Batting (NO ZERO)
                runs = batting_score(name, role)
                balls = max(1, int(runs * random.uniform(0.8, 1.4)))

                safe_request("POST", f"{API_URL}/performances/batting", json={
                    "match_id": match_id,
                    "player_id": pid,
                    "runs": runs,
                    "balls_faced": balls
                }, headers=HEADERS)

                # -------- Bowling (ALL GET ENTRY)
                overs, wkts, conc = bowling_figures(name, role)
                if overs == 0:
                    overs = round(random.uniform(0.1, 1.0), 1)
                    conc = random.randint(3, 12)

                safe_request("POST", f"{API_URL}/performances/bowling", json={
                    "match_id": match_id,
                    "player_id": pid,
                    "overs": overs,
                    "wickets": wkts,
                    "runs_conceded": conc
                }, headers=HEADERS)

        time.sleep(0.3)


def get_or_create_team(team_name):
    # Try creating
    r = safe_request("POST", f"{API_URL}/teams", json={"name": team_name}, headers=HEADERS)
    data = get_json(r)

    if data and data.get("success"):
        return data["team_id"]

    # If already exists → fetch
    r = safe_request("GET", f"{API_URL}/teams")
    data = get_json(r)

    if data and data.get("success"):
        for t in data["teams"]:
            if t["name"].lower() == team_name.lower():
                return t["id"]

    raise Exception(f"❌ Unable to create or fetch team: {team_name}")

# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    print("🏏 CRICKET COACH PRO – FULL REALISTIC DATA (20 MATCHES)\n")

    team_info = {}
    all_players = {}

    for team, plist in TEAMS.items():
       
        tid = get_or_create_team(team)

        for name, role in plist:
            safe_request("POST", f"{API_URL}/players", json={
                "name": name,
                "role": role,
                "team_id": tid
            }, headers=HEADERS)

        r = safe_request("GET", f"{API_URL}/players?team_id={tid}")
        players = get_json(r)["players"]

        team_info[team] = tid
        all_players[team] = {p["name"]: p["id"] for p in players}

    create_matches(team_info, all_players)

    print("\n✅ DONE")
    print("• 20 matches")
    print("• No zero scores")
    print("• Elite bias applied")
    print("• Analytics & ML safe")
