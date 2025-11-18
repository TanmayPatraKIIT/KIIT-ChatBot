"""
Seed basic KIIT data
"""
from database import SessionLocal, Notice, Course, init_db


def seed_basic_data():
    """Seed database with basic KIIT information"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Notice).count() > 0:
            print("Database already seeded, skipping...")
            return
        
        # KIIT Basic Information
        notices = [
            Notice(
                title="About KIIT University",
                content="KIIT (Kalinga Institute of Industrial Technology) is a deemed-to-be-university located in Bhubaneswar, Odisha, India. Established in 1992 by Dr. Achyuta Samanta, KIIT has grown into one of India's premier institutions. The university offers undergraduate, postgraduate, and doctoral programs across various disciplines including engineering, medicine, law, management, and humanities.",
                source_type="basic_info",
                url="https://kiit.ac.in/about"
            ),
            Notice(
                title="KIIT Campus Location",
                content="KIIT University main campus is located at Patia, Bhubaneswar, Odisha 751024, India. The campus spans over 25 square kilometers and houses state-of-the-art facilities including modern classrooms, laboratories, libraries, sports complexes, and hostels.",
                source_type="basic_info"
            ),
            Notice(
                title="KIIT Accreditation",
                content="KIIT University has been accredited with A++ grade by NAAC (National Assessment and Accreditation Council). It is also recognized by UGC and has received various rankings from NIRF (National Institutional Ranking Framework). The university is known for its quality education and research output.",
                source_type="basic_info"
            ),
            Notice(
                title="KIIT Admissions",
                content="KIIT conducts its own entrance examination called KIITEE (KIIT Entrance Examination) for admission to various undergraduate and postgraduate programs. The university also accepts national level examination scores like JEE Main, NEET, CAT, and others depending on the program.",
                source_type="admissions"
            ),
            Notice(
                title="KIIT Facilities",
                content="KIIT provides world-class facilities including: 24/7 library access, advanced laboratories, sports facilities (cricket, football, basketball, tennis), swimming pool, gym, hospital with 24/7 medical facilities, wi-fi enabled campus, modern hostels with all amenities, food courts and canteens.",
                source_type="facilities"
            ),
        ]
        
        # KIIT Courses
        courses = [
            Course(
                name="Bachelor of Technology (B.Tech)",
                code="BTECH",
                description="4-year undergraduate program in engineering and technology",
                department="School of Engineering",
                duration="4 years",
                eligibility="10+2 with Physics, Chemistry, and Mathematics. Minimum 60% marks."
            ),
            Course(
                name="Computer Science and Engineering",
                code="CSE",
                description="Comprehensive program covering software development, algorithms, data structures, AI, machine learning, and emerging technologies",
                department="School of Computer Engineering",
                duration="4 years",
                eligibility="B.Tech program with specialization in Computer Science"
            ),
            Course(
                name="Electronics and Communication Engineering",
                code="ECE",
                description="Program focusing on electronics, telecommunications, signal processing, and embedded systems",
                department="School of Electronics Engineering",
                duration="4 years",
                eligibility="B.Tech program with specialization in Electronics"
            ),
            Course(
                name="Mechanical Engineering",
                code="ME",
                description="Traditional engineering discipline covering thermodynamics, mechanics, manufacturing, and design",
                department="School of Mechanical Engineering",
                duration="4 years",
                eligibility="B.Tech program with specialization in Mechanical Engineering"
            ),
            Course(
                name="Master of Business Administration (MBA)",
                code="MBA",
                description="2-year postgraduate program in management and business administration",
                department="KIIT School of Management",
                duration="2 years",
                eligibility="Bachelor's degree in any discipline with minimum 50% marks. CAT/MAT/XAT scores"
            ),
            Course(
                name="Bachelor of Computer Applications (BCA)",
                code="BCA",
                description="3-year undergraduate program in computer applications and software development",
                department="School of Computer Applications",
                duration="3 years",
                eligibility="10+2 with Mathematics. Minimum 50% marks."
            ),
            Course(
                name="Master of Technology (M.Tech)",
                code="MTECH",
                description="2-year postgraduate program in various engineering specializations",
                department="School of Engineering",
                duration="2 years",
                eligibility="B.Tech/BE in relevant discipline with minimum 60% marks. GATE score preferred."
            ),
            Course(
                name="Bachelor of Science (B.Sc)",
                code="BSC",
                description="3-year undergraduate program in various science disciplines",
                department="School of Applied Sciences",
                duration="3 years",
                eligibility="10+2 with Science stream. Minimum 50% marks."
            ),
        ]
        
        db.add_all(notices)
        db.add_all(courses)
        db.commit()
        
        print(f"✅ Seeded {len(notices)} notices and {len(courses)} courses")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Seeding data...")
    seed_basic_data()
    print("Done!")
