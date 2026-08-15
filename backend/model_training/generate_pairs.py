import sys
sys.path.append("..")

from database import SessionLocal
from models.db_models import FeedbackItem

# Manually defined similar pairs based on your domain knowledge
SIMILAR_PAIRS = [
    # WiFi / Internet
    ("wifi is bad", "internet not working"),
    ("wifi is terrible", "network connection is poor"),
    ("wifi speed is slow", "internet is very slow"),
    ("wifi signal is weak", "internet keeps dropping"),
    ("wifi not working in lab", "internet doesn't work in class"),
    ("wifi adipoli pora", "internet slow aanu"),
    ("net speed kuravaan", "wifi connection illa"),
    ("internet connectivity poor", "network not available in lab"),
    ("wifi password not working", "cant connect to internet"),
    ("broadband speed is very low", "internet bandwidth is insufficient"),
    

    # Canteen / Food
    ("canteen food is bad", "mess food quality is poor"),
    ("food in canteen is cold", "mess serves stale food"),
    ("canteen food quality dropped", "mess food is not good"),
    ("lunch options are limited", "mess menu needs improvement"),
    ("food is tasteless in canteen", "mess food has no quality"),
    ("mess food karyam illa", "canteen quality poor aanu"),
    ("food waste aanu canteen il", "mess serve cheyunnathu kollilla"),
    ("breakfast options are very limited", "morning food choices are few"),
    ("canteen prices are too high", "mess food is overpriced"),
    ("food hygiene in canteen is poor", "mess cleanliness is bad"),

    # Faculty / Teachers
    ("teachers don't finish syllabus", "faculty not completing portions"),
    ("some lecturers are not available", "teachers skip office hours"),
    ("faculty attendance is poor", "teachers don't come to lab"),
    ("teaching quality needs improvement", "lecturers need better methods"),
    ("sir class edukkunilla", "teacher absent aanu"),
    ("faculty not responsive to doubts", "teachers dont answer questions"),
    ("some professors favor certain students", "teacher bias is a problem"),
    ("lab instructor not present", "practical session has no supervision"),
    ("teacher explains too fast", "lectures are hard to follow"),

    # Classroom / Infrastructure
    ("projector not working in class", "classroom equipment is broken"),
    ("lab equipment is outdated", "computers in lab are old"),
    ("classroom is dusty", "lab needs cleaning"),
    ("library closes too early", "library timing should be extended"),
    ("hostel wifi speed slow", "internet in hostel is bad"),
    ("computer lab systems are slow", "lab PCs are outdated"),
    ("ac not working in classroom", "class room is too hot"),
    ("drinking water facility is poor", "water purifier not working"),
    ("parking space is insufficient", "no proper parking area"),


]

# Dissimilar pairs — different complaint categories
DISSIMILAR_PAIRS = [
    ("wifi is bad", "canteen food is bad"),
    ("internet not working", "teachers don't finish syllabus"),
    ("mess food quality poor", "lab equipment is outdated"),
    ("faculty attendance poor", "wifi signal is weak"),
    ("library closes early", "canteen food is cold"),
    ("projector not working", "internet keeps dropping"),
    ("classroom is dusty", "mess food is tasteless"),
    ("teaching quality poor", "wifi speed is slow"),
    ("wifi is bad", "library books are old"),
    ("canteen food poor", "parking is insufficient"),
    ("teacher absent", "water facility poor"),
    ("internet slow", "ac not working"),
    ("lab equipment old", "canteen prices high"),
    ("hostel wifi bad", "teacher explains fast"),
    ("library noisy", "mess food hygiene poor"),
    ("parking insufficient", "faculty not responsive"),
]

def generate_training_csv():
    import csv

    with open("training_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text1", "text2", "label"])

        for t1, t2 in SIMILAR_PAIRS:
            writer.writerow([t1, t2, 1.0])
            # Augment — also write reversed
            writer.writerow([t2, t1, 1.0])

        for t1, t2 in DISSIMILAR_PAIRS:
            writer.writerow([t1, t2, 0.0])
            writer.writerow([t2, t1, 0.0])

    print(f"Generated {(len(SIMILAR_PAIRS) + len(DISSIMILAR_PAIRS)) * 2} training pairs")
    print("Saved to training_data.csv")

if __name__ == "__main__":
    generate_training_csv()