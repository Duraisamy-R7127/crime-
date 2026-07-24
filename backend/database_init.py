import os
import random
from datetime import datetime, timedelta
from database import engine, Base, SessionLocal
import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TN_DISTRICTS = [
    {"name": "Chennai", "lat": 13.0827, "lng": 80.2707, "pop": 7088000},
    {"name": "Coimbatore", "lat": 11.0168, "lng": 76.9558, "pop": 3458000},
    {"name": "Madurai", "lat": 9.9252, "lng": 78.1198, "pop": 3038000},
    {"name": "Tiruchirappalli", "lat": 10.7905, "lng": 78.7047, "pop": 2722000},
    {"name": "Salem", "lat": 11.6643, "lng": 78.1460, "pop": 3482000},
    {"name": "Tirunelveli", "lat": 8.7139, "lng": 77.7567, "pop": 1665000},
    {"name": "Erode", "lat": 11.3410, "lng": 77.7172, "pop": 2251000},
    {"name": "Vellore", "lat": 12.9165, "lng": 79.1325, "pop": 1614000},
    {"name": "Thoothukudi", "lat": 8.7642, "lng": 78.1348, "pop": 1750000},
    {"name": "Tiruppur", "lat": 11.1085, "lng": 77.3411, "pop": 2479000},
    {"name": "Thanjavur", "lat": 10.7870, "lng": 79.1378, "pop": 2405000},
    {"name": "Dindigul", "lat": 10.3673, "lng": 77.9803, "pop": 2159000},
    {"name": "Kanchipuram", "lat": 12.8185, "lng": 79.6947, "pop": 1166000},
    {"name": "Chengalpattu", "lat": 12.6841, "lng": 79.9758, "pop": 2556000},
    {"name": "Villupuram", "lat": 11.9401, "lng": 79.4861, "pop": 3458000},
    {"name": "Cuddalore", "lat": 11.7480, "lng": 79.7714, "pop": 2605000},
    {"name": "Tiruvannamalai", "lat": 12.2253, "lng": 79.0747, "pop": 2464000},
    {"name": "Kanyakumari", "lat": 8.0883, "lng": 77.5385, "pop": 1870000},
    {"name": "Nilgiris", "lat": 11.4166, "lng": 76.6953, "pop": 735000},
    {"name": "Krishnagiri", "lat": 12.5186, "lng": 78.2137, "pop": 1879000},
    {"name": "Dharmapuri", "lat": 12.1211, "lng": 78.1582, "pop": 1506000},
    {"name": "Namakkal", "lat": 11.2189, "lng": 78.1674, "pop": 1726000},
    {"name": "Karur", "lat": 10.9601, "lng": 78.0766, "pop": 1064000},
    {"name": "Perambalur", "lat": 11.2342, "lng": 78.8821, "pop": 565000},
    {"name": "Ariyalur", "lat": 11.1401, "lng": 79.0786, "pop": 754000},
    {"name": "Nagapattinam", "lat": 10.7672, "lng": 79.8449, "pop": 1616000},
    {"name": "Tiruvarur", "lat": 10.7720, "lng": 79.6367, "pop": 1264000},
    {"name": "Pudukkottai", "lat": 10.3797, "lng": 78.8205, "pop": 1618000},
    {"name": "Sivaganga", "lat": 9.8433, "lng": 78.4809, "pop": 1339000},
    {"name": "Ramanathapuram", "lat": 9.3582, "lng": 78.8321, "pop": 1353000},
    {"name": "Virudhunagar", "lat": 9.5872, "lng": 77.9514, "pop": 1942000},
    {"name": "Theni", "lat": 10.0104, "lng": 77.4768, "pop": 1245000},
    {"name": "Mayiladuthurai", "lat": 11.1026, "lng": 79.6543, "pop": 918000},
    {"name": "Tenkasi", "lat": 8.9594, "lng": 77.3161, "pop": 1407000},
    {"name": "Kallakurichi", "lat": 11.7383, "lng": 78.9639, "pop": 1370000},
    {"name": "Ranipet", "lat": 12.9273, "lng": 79.3323, "pop": 1210000},
    {"name": "Tirupathur", "lat": 12.4984, "lng": 78.5670, "pop": 1111000},
    {"name": "Tiruvallur", "lat": 13.1432, "lng": 79.9103, "pop": 3728000}
]

CRIME_TYPES = ["Theft", "Cyber Fraud", "Assault", "Chain Snatching", "Robbery", "Drug Crime", "Missing Persons", "Traffic Violations", "Women Safety Cases", "Violence"]
CRIME_CATEGORIES = ["Property", "Cyber", "Violent", "Property", "Violent", "Narcotics", "Misc", "Traffic", "Women Safety", "Violent"]

def get_mock_city_and_area(district_name):
    if district_name == "Chennai":
        cities = ["Chennai City"]
        areas = ["Adyar", "Mylapore", "T Nagar", "Anna Nagar", "Velachery", "Guindy", "Royapettah"]
    elif district_name == "Coimbatore":
        cities = ["Coimbatore City", "Pollachi", "Mettupalayam"]
        areas = ["Gandhipuram", "RS Puram", "Peelamedu", "Ukkadam", "Singanallur"]
    elif district_name == "Madurai":
        cities = ["Madurai City", "Usilampatti", "Melur"]
        areas = ["Anna Nagar", "KK Nagar", "Tallakulam", "Thirunagar"]
    else:
        cities = [f"{district_name} Town", f"{district_name} Rural"]
        areas = ["North Zone", "South Zone", "East Zone", "West Zone", "Central Zone"]
        
    city = random.choice(cities)
    area = random.choice(areas)
    station = f"{area} PS"
    return city, area, station

def init_db():
    if os.path.exists("crimevision.db"):
        os.remove("crimevision.db")
        print("Dropped old database.")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Add Users
    hashed_pw = pwd_context.hash("admin123")
    admin = models.User(username="admin", email="admin@tnpolice.gov.in", hashed_password=hashed_pw, full_name="State Command Admin", role=models.RoleEnum.super_admin, state="Tamil Nadu")
    db.add(admin)

    # 2. Add Districts
    db_districts = []
    for d in TN_DISTRICTS:
        dist = models.District(name=d["name"], population=d["pop"], latitude=d["lat"], longitude=d["lng"])
        db.add(dist)
        db_districts.append(dist)
    db.commit()

    # 3. Legal Sections
    sections = [
        models.LegalSection(crime_type="Murder", category="Offences against Human Body", ipc_section="302", bns_section="103", punishment="Death or imprisonment for life, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Whoever commits murder shall be punished with death or imprisonment for life.", investigation_procedure="Standard homicide investigation", court_jurisdiction="Sessions Court", evidence_required="Forensics, Witness testimonies", legal_notes="Exceptions: culpable homicide not amounting to murder"),
        models.LegalSection(crime_type="Culpable Homicide", category="Offences against Human Body", ipc_section="304", bns_section="105", punishment="Imprisonment for life, or imprisonment up to 10 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Causing death by doing an act with the intention of causing death, or with the intention of causing such bodily injury as is likely to cause death.", investigation_procedure="Standard homicide investigation", court_jurisdiction="Sessions Court", evidence_required="Forensics, Witness testimonies", legal_notes=""),
        models.LegalSection(crime_type="Causing Death by Negligence", category="Offences against Human Body", ipc_section="304A", bns_section="106", punishment="Imprisonment up to 5 years, or fine, or both", is_bailable=True, is_cognizable=True, is_compoundable=False, description="Causing death by rash or negligent act not amounting to culpable homicide.", investigation_procedure="Accident investigation", court_jurisdiction="Magistrate First Class", evidence_required="Accident reports, Witness testimonies", legal_notes=""),
        models.LegalSection(crime_type="Attempt to Murder", category="Offences against Human Body", ipc_section="307", bns_section="109", punishment="Imprisonment up to 10 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Doing any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder.", investigation_procedure="Standard investigation", court_jurisdiction="Sessions Court", evidence_required="Medical reports, Witness testimonies", legal_notes=""),
        models.LegalSection(crime_type="Voluntarily Causing Grievous Hurt", category="Offences against Human Body", ipc_section="325", bns_section="116", punishment="Imprisonment up to 7 years, and fine", is_bailable=True, is_cognizable=True, is_compoundable=True, description="Voluntarily causing grievous hurt.", investigation_procedure="Medical examination", court_jurisdiction="Magistrate", evidence_required="Medical reports", legal_notes="Compoundable with permission of the court"),
        models.LegalSection(crime_type="Kidnapping", category="Offences against Human Body", ipc_section="363", bns_section="137", punishment="Imprisonment up to 7 years, and fine", is_bailable=True, is_cognizable=True, is_compoundable=False, description="Kidnapping any person from India or from lawful guardianship.", investigation_procedure="Missing person investigation", court_jurisdiction="Magistrate First Class", evidence_required="Witness testimonies, CCTV footage", legal_notes=""),
        models.LegalSection(crime_type="Rape", category="Offences against Women & Children", ipc_section="376", bns_section="64", punishment="Rigorous imprisonment not less than 10 years, which may extend to life, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Committing rape.", investigation_procedure="Specialized investigation by female officer", court_jurisdiction="Sessions Court", evidence_required="Medical reports, Statement of victim", legal_notes=""),
        models.LegalSection(crime_type="Sexual Harassment", category="Offences against Women & Children", ipc_section="354A", bns_section="74", punishment="Imprisonment up to 3 years, or fine, or both", is_bailable=True, is_cognizable=True, is_compoundable=False, description="Making sexually coloured remarks, physical contact, or demanding sexual favours.", investigation_procedure="Specialized investigation", court_jurisdiction="Magistrate", evidence_required="Statement of victim, digital evidence", legal_notes=""),
        models.LegalSection(crime_type="Voyeurism", category="Offences against Women & Children", ipc_section="354C", bns_section="77", punishment="Imprisonment up to 3 years, and fine (first conviction)", is_bailable=True, is_cognizable=True, is_compoundable=False, description="Watching or capturing image of a woman engaging in a private act.", investigation_procedure="Digital forensics", court_jurisdiction="Magistrate", evidence_required="Digital evidence, devices", legal_notes=""),
        models.LegalSection(crime_type="Stalking", category="Offences against Women & Children", ipc_section="354D", bns_section="78", punishment="Imprisonment up to 3 years, and fine (first conviction)", is_bailable=True, is_cognizable=True, is_compoundable=False, description="Following a woman and contacting, or attempting to contact such woman repeatedly.", investigation_procedure="Cyber investigation", court_jurisdiction="Magistrate", evidence_required="Digital evidence, witness", legal_notes=""),
        models.LegalSection(crime_type="Theft", category="Property Offences", ipc_section="379", bns_section="303", punishment="Imprisonment up to 3 years, or fine, or both", is_bailable=False, is_cognizable=True, is_compoundable=True, description="Dishonestly taking any movable property out of the possession of any person.", investigation_procedure="Standard property investigation", court_jurisdiction="Magistrate", evidence_required="Recovery of stolen goods, CCTV", legal_notes="Compoundable if property value is low"),
        models.LegalSection(crime_type="Extortion", category="Property Offences", ipc_section="384", bns_section="308", punishment="Imprisonment up to 3 years, or fine, or both", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Intentionally putting any person in fear of any injury to that person, and thereby dishonestly inducing the person so put in fear to deliver to any person any property.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate", evidence_required="Call records, Witness", legal_notes=""),
        models.LegalSection(crime_type="Robbery", category="Property Offences", ipc_section="392", bns_section="309", punishment="Rigorous imprisonment up to 10 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Theft or extortion involving fear of instant death, hurt, or wrongful restraint.", investigation_procedure="Specialized investigation", court_jurisdiction="Magistrate First Class", evidence_required="Recovery of goods, CCTV, Witness", legal_notes=""),
        models.LegalSection(crime_type="Dacoity", category="Property Offences", ipc_section="395", bns_section="310", punishment="Imprisonment for life, or rigorous imprisonment up to 10 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Five or more persons conjointly committing or attempting to commit robbery.", investigation_procedure="Special task force", court_jurisdiction="Sessions Court", evidence_required="Recovery of goods, weapons, CCTV", legal_notes=""),
        models.LegalSection(crime_type="Criminal Breach of Trust", category="Property Offences", ipc_section="406", bns_section="316", punishment="Imprisonment up to 3 years, or fine, or both", is_bailable=False, is_cognizable=True, is_compoundable=True, description="Dishonest misappropriation or conversion of property entrusted to a person.", investigation_procedure="Financial investigation", court_jurisdiction="Magistrate First Class", evidence_required="Documentary evidence, Bank statements", legal_notes=""),
        models.LegalSection(crime_type="Cheating and Dishonestly Inducing Delivery of Property", category="Property Offences", ipc_section="420", bns_section="318", punishment="Imprisonment up to 7 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=True, description="Cheating and thereby dishonestly inducing the person deceived to deliver any property.", investigation_procedure="Financial investigation", court_jurisdiction="Magistrate First Class", evidence_required="Documentary evidence, Bank statements", legal_notes="Compoundable with permission of the court"),
        models.LegalSection(crime_type="Mischief", category="Property Offences", ipc_section="426", bns_section="324", punishment="Imprisonment up to 3 months, or fine, or both", is_bailable=True, is_cognizable=False, is_compoundable=True, description="Causing destruction of property or any such change in property as destroys or diminishes its value or utility.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate", evidence_required="Damage reports, Witness", legal_notes=""),
        models.LegalSection(crime_type="Criminal Trespass", category="Property Offences", ipc_section="447", bns_section="329", punishment="Imprisonment up to 3 months, or fine up to Rs. 500, or both", is_bailable=True, is_cognizable=True, is_compoundable=True, description="Entering into or upon property in the possession of another with intent to commit an offence.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate", evidence_required="Witness, CCTV", legal_notes=""),
        models.LegalSection(crime_type="House-breaking by Night", category="Property Offences", ipc_section="456", bns_section="331", punishment="Imprisonment up to 3 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Committing house-breaking after sunset and before sunrise.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate", evidence_required="Forensics, CCTV, Witness", legal_notes=""),
        models.LegalSection(crime_type="Forgery", category="Economic Offences", ipc_section="465", bns_section="336", punishment="Imprisonment up to 2 years, or fine, or both", is_bailable=True, is_cognizable=False, is_compoundable=False, description="Making any false document or false electronic record with intent to cause damage or injury.", investigation_procedure="Document forensics", court_jurisdiction="Magistrate First Class", evidence_required="Forensic analysis of documents", legal_notes=""),
        models.LegalSection(crime_type="Counterfeiting Currency Notes", category="Economic Offences", ipc_section="489A", bns_section="178", punishment="Imprisonment for life, or imprisonment up to 10 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Counterfeiting or knowingly performing any part of the process of counterfeiting any currency note.", investigation_procedure="Special investigation", court_jurisdiction="Sessions Court", evidence_required="Recovery of counterfeit notes, machinery", legal_notes=""),
        models.LegalSection(crime_type="Defamation", category="Offences against Reputation", ipc_section="500", bns_section="356", punishment="Simple imprisonment up to 2 years, or fine, or both", is_bailable=True, is_cognizable=False, is_compoundable=True, description="Making or publishing any imputation concerning any person intending to harm the reputation of such person.", investigation_procedure="Non-cognizable procedure", court_jurisdiction="Magistrate First Class", evidence_required="Documentary evidence, Witness", legal_notes="Compoundable"),
        models.LegalSection(crime_type="Criminal Intimidation", category="Offences against Reputation", ipc_section="506", bns_section="351", punishment="Imprisonment up to 2 years, or fine, or both", is_bailable=True, is_cognizable=False, is_compoundable=True, description="Threatening another with any injury to his person, reputation or property.", investigation_procedure="Non-cognizable procedure", court_jurisdiction="Magistrate", evidence_required="Witness, Call records", legal_notes="Compoundable"),
        models.LegalSection(crime_type="Public Nuisance", category="Offences against Public Tranquility", ipc_section="268", bns_section="270", punishment="Fine up to Rs. 200", is_bailable=True, is_cognizable=False, is_compoundable=False, description="Doing any act or is guilty of an illegal omission which causes any common injury, danger or annoyance to the public.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate", evidence_required="Witness, Police report", legal_notes=""),
        models.LegalSection(crime_type="Rioting", category="Offences against Public Tranquility", ipc_section="147", bns_section="191", punishment="Imprisonment up to 2 years, or fine, or both", is_bailable=True, is_cognizable=True, is_compoundable=False, description="Using force or violence by an unlawful assembly.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate", evidence_required="Video evidence, Witness", legal_notes=""),
        models.LegalSection(crime_type="Affray", category="Offences against Public Tranquility", ipc_section="160", bns_section="194", punishment="Imprisonment up to 1 month, or fine up to Rs. 100, or both", is_bailable=True, is_cognizable=False, is_compoundable=False, description="Two or more persons fighting in a public place and disturbing the public peace.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate", evidence_required="Witness, Police report", legal_notes=""),
        models.LegalSection(crime_type="Bribery", category="Offences by Public Servants", ipc_section="171E", bns_section="170", punishment="Imprisonment up to 1 year, or fine, or both", is_bailable=True, is_cognizable=False, is_compoundable=False, description="Giving or accepting a gratification as a motive or reward for doing or forbearing to do any official act.", investigation_procedure="Anti-corruption investigation", court_jurisdiction="Magistrate First Class", evidence_required="Call records, Recovery of bribe", legal_notes=""),
        models.LegalSection(crime_type="False Evidence", category="Offences against Public Justice", ipc_section="193", bns_section="227", punishment="Imprisonment up to 7 years, and fine", is_bailable=True, is_cognizable=False, is_compoundable=False, description="Intentionally giving false evidence in any stage of a judicial proceeding.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate First Class", evidence_required="Court records, Witness", legal_notes=""),
        models.LegalSection(crime_type="Harbouring an Offender", category="Offences against Public Justice", ipc_section="212", bns_section="239", punishment="Imprisonment for various terms depending on the offence, and fine", is_bailable=True, is_cognizable=True, is_compoundable=False, description="Harbouring or concealing a person whom he knows or has reason to believe to be the offender.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate First Class", evidence_required="Witness, Call records", legal_notes=""),
        models.LegalSection(crime_type="Causing Miscarriage", category="Offences against Human Body", ipc_section="312", bns_section="88", punishment="Imprisonment up to 3 years, or fine, or both", is_bailable=True, is_cognizable=False, is_compoundable=False, description="Voluntarily causing a woman with child to miscarry.", investigation_procedure="Medical investigation", court_jurisdiction="Magistrate First Class", evidence_required="Medical reports, Witness", legal_notes=""),
        models.LegalSection(crime_type="Dowry Death", category="Offences against Women & Children", ipc_section="304B", bns_section="80", punishment="Imprisonment not less than 7 years, which may extend to life", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Death of a woman caused by burns or bodily injury or occurs otherwise than under normal circumstances within 7 years of her marriage, and it is shown that soon before her death she was subjected to cruelty or harassment by her husband or any relative of her husband for, or in connection with, any demand for dowry.", investigation_procedure="Special investigation", court_jurisdiction="Sessions Court", evidence_required="Medical reports, Witness", legal_notes=""),
        models.LegalSection(crime_type="Cruelty by Husband or Relatives", category="Offences against Women & Children", ipc_section="498A", bns_section="85", punishment="Imprisonment up to 3 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Husband or relative of husband of a woman subjecting her to cruelty.", investigation_procedure="Special investigation", court_jurisdiction="Magistrate First Class", evidence_required="Medical reports, Witness", legal_notes=""),
        models.LegalSection(crime_type="Adultery (Decriminalized, noted for reference)", category="Offences against Marriage", ipc_section="497", bns_section="N/A", punishment="N/A", is_bailable=True, is_cognizable=False, is_compoundable=True, description="Sexual intercourse with a person who is and whom he knows or has reason to believe to be the wife of another man. (Struck down by Supreme Court)", investigation_procedure="N/A", court_jurisdiction="N/A", evidence_required="N/A", legal_notes="Decriminalized"),
        models.LegalSection(crime_type="Bigamy", category="Offences against Marriage", ipc_section="494", bns_section="82", punishment="Imprisonment up to 7 years, and fine", is_bailable=True, is_cognizable=False, is_compoundable=True, description="Marrying again during lifetime of husband or wife.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate First Class", evidence_required="Marriage certificates, Witness", legal_notes="Compoundable with permission of the court"),
        models.LegalSection(crime_type="Criminal Conspiracy", category="General Offences", ipc_section="120B", bns_section="61", punishment="Punished in the same manner as if he had abetted such offence", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Agreement between two or more persons to commit an illegal act.", investigation_procedure="Special investigation", court_jurisdiction="Magistrate First Class/Sessions Court", evidence_required="Call records, Witness", legal_notes=""),
        models.LegalSection(crime_type="Sedition", category="Offences against the State", ipc_section="124A", bns_section="152", punishment="Imprisonment for life, to which fine may be added, or with imprisonment which may extend to 3 years, to which fine may be added, or with fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Words, either spoken or written, or by signs, or by visible representation, or otherwise, brings or attempts to bring into hatred or contempt, or excites or attempts to excite disaffection towards the Government.", investigation_procedure="Special investigation", court_jurisdiction="Sessions Court", evidence_required="Video evidence, Witness", legal_notes=""),
        models.LegalSection(crime_type="Waging War against the Government", category="Offences against the State", ipc_section="121", bns_section="147", punishment="Death, or imprisonment for life, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Wages war against the Government of India, or attempts to wage such war, or abets the waging of such war.", investigation_procedure="National Investigation Agency (NIA)", court_jurisdiction="Sessions Court", evidence_required="Weapons, Call records, Witness", legal_notes=""),
        models.LegalSection(crime_type="Cyber Terrorism", category="Cyber Crimes", ipc_section="IT Act 66F", bns_section="111", punishment="Imprisonment which may extend to imprisonment for life", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Intent to threaten the unity, integrity, security or sovereignty of India or to strike terror in the people by denying access to authorized personnel to a computer resource, attempting to penetrate or access a computer resource without authorization, etc.", investigation_procedure="Cyber cell investigation", court_jurisdiction="Sessions Court", evidence_required="Digital forensics, Network logs", legal_notes=""),
        models.LegalSection(crime_type="Identity Theft", category="Cyber Crimes", ipc_section="IT Act 66C", bns_section="319", punishment="Imprisonment up to 3 years, and fine up to Rs. 1 Lakh", is_bailable=True, is_cognizable=True, is_compoundable=False, description="Fraudulently or dishonestly makes use of the electronic signature, password or any other unique identification feature of any other person.", investigation_procedure="Cyber cell investigation", court_jurisdiction="Magistrate First Class", evidence_required="Digital evidence, IP logs", legal_notes=""),
        models.LegalSection(crime_type="Cheating by Personation using Computer", category="Cyber Crimes", ipc_section="IT Act 66D", bns_section="319", punishment="Imprisonment up to 3 years, and fine up to Rs. 1 Lakh", is_bailable=True, is_cognizable=True, is_compoundable=False, description="Cheating by personation by means of any communication device or computer resource.", investigation_procedure="Cyber cell investigation", court_jurisdiction="Magistrate First Class", evidence_required="Digital evidence, IP logs", legal_notes=""),
        models.LegalSection(crime_type="Publishing Obscene Material", category="Cyber Crimes", ipc_section="IT Act 67", bns_section="292", punishment="Imprisonment up to 3 years, and fine up to Rs. 5 Lakhs (first conviction)", is_bailable=True, is_cognizable=True, is_compoundable=False, description="Publishes or transmits or causes to be published or transmitted in the electronic form, any material which is lascivious or appeals to the prurient interest.", investigation_procedure="Cyber cell investigation", court_jurisdiction="Magistrate First Class", evidence_required="Digital evidence, URLs", legal_notes=""),
        models.LegalSection(crime_type="Child Pornography", category="Cyber Crimes", ipc_section="IT Act 67B", bns_section="79", punishment="Imprisonment up to 5 years, and fine up to Rs. 10 Lakhs (first conviction)", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Publishing or transmitting of material depicting children in sexually explicit act, etc., in electronic form.", investigation_procedure="Cyber cell investigation", court_jurisdiction="Magistrate First Class", evidence_required="Digital evidence, URLs", legal_notes=""),
        models.LegalSection(crime_type="Drug Possession (Small Quantity)", category="Narcotics", ipc_section="NDPS 27", bns_section="NDPS 27", punishment="Imprisonment up to 1 year, or fine up to Rs. 20,000, or both", is_bailable=True, is_cognizable=True, is_compoundable=False, description="Consumption of any narcotic drug or psychotropic substance.", investigation_procedure="Narcotics investigation", court_jurisdiction="Magistrate First Class", evidence_required="Chemical analysis, Seizure memo", legal_notes=""),
        models.LegalSection(crime_type="Drug Trafficking (Commercial Quantity)", category="Narcotics", ipc_section="NDPS 21(c)", bns_section="NDPS 21(c)", punishment="Rigorous imprisonment not less than 10 years, which may extend to 20 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Manufacture, possession, sale, purchase, transport, import inter-State, export inter-State or use of manufactured drugs.", investigation_procedure="Narcotics investigation", court_jurisdiction="Special Court (NDPS)", evidence_required="Chemical analysis, Seizure memo, Call records", legal_notes=""),
        models.LegalSection(crime_type="Human Trafficking", category="Organized Crime", ipc_section="370", bns_section="143", punishment="Rigorous imprisonment not less than 7 years, which may extend to 10 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Recruiting, transporting, harbouring, transferring, or receiving a person for the purpose of exploitation.", investigation_procedure="Special investigation", court_jurisdiction="Sessions Court", evidence_required="Witness, Call records, Financial trails", legal_notes=""),
        models.LegalSection(crime_type="Money Laundering", category="Economic Offences", ipc_section="PMLA 3", bns_section="PMLA 3", punishment="Rigorous imprisonment not less than 3 years, which may extend to 7 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Directly or indirectly attempting to indulge or knowingly assisting or knowingly is a party or is actually involved in any process or activity connected with the proceeds of crime.", investigation_procedure="Enforcement Directorate (ED)", court_jurisdiction="Special Court (PMLA)", evidence_required="Financial records, Bank statements", legal_notes=""),
        models.LegalSection(crime_type="Smuggling", category="Economic Offences", ipc_section="Customs Act 135", bns_section="Customs Act 135", punishment="Imprisonment up to 7 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Evasion of duty or prohibitions.", investigation_procedure="Customs investigation", court_jurisdiction="Magistrate First Class", evidence_required="Seizure memo, Statements", legal_notes=""),
        models.LegalSection(crime_type="Arms Act Violation", category="Special Acts", ipc_section="Arms Act 25", bns_section="Arms Act 25", punishment="Imprisonment not less than 1 year, which may extend to 3 years, and fine", is_bailable=False, is_cognizable=True, is_compoundable=False, description="Acquiring, possessing or carrying any prohibited arms or prohibited ammunition.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate First Class", evidence_required="Seizure memo, Ballistic report", legal_notes=""),
        models.LegalSection(crime_type="Animal Cruelty", category="Special Acts", ipc_section="PCA Act 11", bns_section="PCA Act 11", punishment="Fine up to Rs. 50 (first offence)", is_bailable=True, is_cognizable=False, is_compoundable=False, description="Treating animals cruelly.", investigation_procedure="Standard investigation", court_jurisdiction="Magistrate", evidence_required="Veterinary reports, Witness", legal_notes=""),
        models.LegalSection(crime_type="Environmental Pollution", category="Special Acts", ipc_section="EPA 15", bns_section="EPA 15", punishment="Imprisonment up to 5 years, or fine up to Rs. 1 Lakh, or both", is_bailable=True, is_cognizable=False, is_compoundable=False, description="Failure to comply with or contravention of any of the provisions of the Environment (Protection) Act.", investigation_procedure="Pollution Control Board", court_jurisdiction="Magistrate First Class", evidence_required="Lab reports, Inspection reports", legal_notes=""),
    ]
    db.add_all(sections)

    # 4. Generate Mock FIRs (1500 historical cases for state-wide)
    firs = []
    criminals = []
    alerts = []
    print("Generating state-wide FIRs, Criminals, and Alerts...")
    for i in range(1, 3001):
        dist = random.choice(db_districts)
        city, area, station = get_mock_city_and_area(dist.name)
        
        ctype_idx = random.randint(0, len(CRIME_TYPES) - 1)
        ctype = CRIME_TYPES[ctype_idx]
        ccat = CRIME_CATEGORIES[ctype_idx]
        
        days_ago = random.randint(0, 1095)
        reported_date = datetime.utcnow() - timedelta(days=days_ago)
        
        status = random.choice([models.StatusEnum.open, models.StatusEnum.investigating, models.StatusEnum.resolved])
        
        # Jitter lat/lng around district center
        lat_jitter = dist.latitude + random.uniform(-0.1, 0.1)
        lng_jitter = dist.longitude + random.uniform(-0.1, 0.1)
        
        fir_num = f"TN-{dist.name[:3].upper()}-2026-{str(i).zfill(6)}"
        
        fir = models.FIR(
            fir_number=fir_num,
            state="Tamil Nadu",
            district=dist.name,
            city=city,
            area=area,
            police_station=station,
            crime_type=ctype,
            crime_category=ccat,
            date_reported=reported_date,
            location_name=f"{area}, {city}",
            latitude=lat_jitter,
            longitude=lng_jitter,
            status=status,
            incident_description=f"Incident of {ctype} reported in {area}, {dist.name}."
        )
        firs.append(fir)
        
        # Generate some criminals
        if i % 10 == 0:
            criminal = models.Criminal(
                name=f"Suspect {i}",
                alias=f"Alias {i}",
                address=f"{area}, {dist.name}",
                crime_history=f"Involved in {ctype}",
                arrest_records="None",
                risk_level=random.choice([models.SeverityEnum.medium, models.SeverityEnum.high, models.SeverityEnum.critical]),
                state="Tamil Nadu",
                district=dist.name,
                city=city,
                area=area,
                police_station=station
            )
            criminals.append(criminal)
            
        # Generate some alerts
        if i % 20 == 0:
            alert = models.Alert(
                message=f"High risk activity: {ctype} in {area}",
                severity=random.choice([models.SeverityEnum.medium, models.SeverityEnum.high]),
                source="AI Model",
                state="Tamil Nadu",
                district=dist.name,
                city=city,
                area=area
            )
            alerts.append(alert)
    
    db.add_all(firs)
    db.add_all(criminals)
    db.add_all(alerts)
    
    # 5. Generate Missing Persons and Emergency Incidents
    print("Generating Missing Persons and Emergencies...")
    missing = []
    emergencies = []
    for i in range(1, 51):
        dist = random.choice(db_districts)
        city, area, station = get_mock_city_and_area(dist.name)
        
        mp = models.MissingPerson(
            name=f"Missing Person {i}",
            age=random.randint(5, 75),
            gender=random.choice(["Male", "Female"]),
            description=f"Last seen at {area}",
            last_seen_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            status=random.choice(["Missing", "Found"]),
            state="Tamil Nadu",
            district=dist.name,
            city=city,
            area=area
        )
        missing.append(mp)
        
        em = models.EmergencyIncident(
            incident_type=random.choice(["Riot", "Fire", "Severe Accident", "Armed Robbery"]),
            description=f"Emergency reported in {area}",
            severity=random.choice([models.SeverityEnum.high, models.SeverityEnum.critical]),
            status=random.choice(["Active", "Responded", "Resolved"]),
            latitude=dist.latitude + random.uniform(-0.05, 0.05),
            longitude=dist.longitude + random.uniform(-0.05, 0.05),
            reported_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 60)),
            state="Tamil Nadu",
            district=dist.name,
            city=city,
            area=area
        )
        emergencies.append(em)
        
    db.add_all(missing)
    db.add_all(emergencies)
    db.commit()

    db.close()
    print("Database fully initialized with Tamil Nadu state data.")

if __name__ == "__main__":
    init_db()
