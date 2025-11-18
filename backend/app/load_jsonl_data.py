"""
Load KIIT data from JSONL files into PostgreSQL database
"""
import json
import os
from app.database import SessionLocal, Notice, Course, init_db
from datetime import datetime


def load_jsonl_file(filepath):
    """Load and parse a JSONL file"""
    data = []
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return data
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def load_placement_data(db):
    """Load placement data from JSONL"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filepath = os.path.join(base_dir, "attached_assets", "kiit_placement_1763445194133.jsonl")
    data = load_jsonl_file(filepath)
    
    notices = []
    for record in data:
        section_id = record.get('section_id', '')
        
        if section_id == 'page':
            notices.append(Notice(
                title=record.get('title', 'KIIT Placement Overview'),
                content=record.get('summary', ''),
                url=record.get('url', ''),
                source_type='placement'
            ))
        
        elif section_id == 'highlights_2024':
            data_obj = record.get('data', {})
            text = f"2024 Placement Highlights:\n- Companies Visited: {data_obj.get('companies_visited', 'N/A')}\n- Job Offers: {data_obj.get('job_offers', 'N/A')}\n- Highest Package: ₹{data_obj.get('highest_package_lakhs', 'N/A')} lakhs"
            notices.append(Notice(
                title='KIIT Placement 2024 Highlights',
                content=text,
                url='https://kiit.ac.in/training-placement/',
                source_type='placement'
            ))
        
        elif section_id == 'year_wise_stats':
            years_data = record.get('years', [])
            stats_text = "KIIT Year-wise Placement Statistics (2014-2024):\n\n"
            for year_obj in years_data:
                stats_text += f"Year {year_obj.get('year', 'N/A')}:\n"
                stats_text += f"  - Companies: {year_obj.get('companies', 'N/A')}\n"
                stats_text += f"  - Job Offers: {year_obj.get('job_offers', 'N/A')}\n"
                stats_text += f"  - Highest Package: ₹{year_obj.get('highest_package_lakhs', 'N/A')} lakhs\n\n"
            
            notices.append(Notice(
                title='KIIT Year-wise Placement Statistics (2014-2024)',
                content=stats_text.strip(),
                url='https://kiit.ac.in/training-placement/',
                source_type='placement_statistics'
            ))
        
        elif section_id == 'kiit_kareer_school':
            notices.append(Notice(
                title=record.get('title', 'KIIT-Kareer School'),
                content=record.get('text', ''),
                url=record.get('read_more_url', 'https://kiit.ac.in'),
                source_type='career_services'
            ))
    
    return notices


def load_courses_data(db):
    """Load courses data from JSONL"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filepath = os.path.join(base_dir, "attached_assets", "kiit_courses_1763445194134.jsonl")
    data = load_jsonl_file(filepath)
    
    courses = []
    for record in data:
        section_id = record.get('section_id', '')
        
        if section_id == 'undergraduate_programs':
            programs = record.get('programs', [])
            for prog in programs:
                courses.append(Course(
                    name=prog.get('name', ''),
                    code=prog.get('name', '').replace(' ', '_').upper(),
                    description=f"{prog.get('name', '')} - {prog.get('duration', '')}. {prog.get('notes', '')}",
                    department='Various Schools',
                    duration=prog.get('duration', ''),
                    eligibility='As per KIIT admission criteria'
                ))
        
        elif section_id == 'schools_sample':
            schools = record.get('schools', [])
            for school_obj in schools:
                school_name = school_obj.get('school', '')
                school_courses = school_obj.get('courses', [])
                
                for course_obj in school_courses:
                    degree = course_obj.get('degree', '')
                    specializations = course_obj.get('specializations', [])
                    
                    if specializations:
                        for spec in specializations:
                            courses.append(Course(
                                name=f"{degree} in {spec}",
                                code=f"{degree}_{spec}".replace(' ', '_').upper(),
                                description=f"{degree} program in {spec} offered by {school_name}",
                                department=school_name,
                                duration=course_obj.get('duration', 'Varies'),
                                eligibility='As per KIIT admission criteria'
                            ))
    
    return courses


def load_ranking_data(db):
    """Load ranking and recognition data from JSONL"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filepath = os.path.join(base_dir, "attached_assets", "kiit_ranking_recognition_1763445194136.jsonl")
    data = load_jsonl_file(filepath)
    
    notices = []
    for record in data:
        section_id = record.get('section_id', '')
        
        if section_id == 'page':
            continue
        
        title = record.get('title', section_id.replace('_', ' ').title())
        
        # Construct content based on available fields
        content_parts = []
        
        if 'rank' in record:
            content_parts.append(f"Rank: {record['rank']}")
        
        if 'text' in record:
            content_parts.append(record['text'])
        
        if 'award_year' in record:
            content_parts.append(f"Year: {record['award_year']}")
        
        if 'sdg_highlights' in record:
            sdg = record['sdg_highlights']
            content_parts.append(f"SDG Highlights: {json.dumps(sdg, indent=2)}")
        
        if 'schools' in record:
            schools_text = "\n".join([f"- {s.get('school', '')}: {s.get('rank', '')}" for s in record.get('schools', [])])
            content_parts.append(f"School Rankings:\n{schools_text}")
        
        if 'items' in record:
            items_text = "\n".join([f"- {item}" for item in record.get('items', [])])
            content_parts.append(items_text)
        
        content = "\n\n".join(content_parts) if content_parts else title
        
        notices.append(Notice(
            title=title,
            content=content,
            url=record.get('url', 'https://kiit.ac.in/about/ranking-recognition/'),
            source_type='ranking'
        ))
    
    return notices


def load_about_data(db):
    """Load about/general KIIT data from JSONL"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filepath = os.path.join(base_dir, "attached_assets", "kiit_about_1763445194137.jsonl")
    data = load_jsonl_file(filepath)
    
    notices = []
    for record in data:
        section_id = record.get('section_id', '')
        
        if section_id == 'page':
            continue
        
        title = record.get('title', section_id.replace('_', ' ').title())
        
        # Construct content
        content_parts = []
        
        if 'text' in record:
            if isinstance(record['text'], list):
                content_parts.append("\n".join([f"• {item}" for item in record['text']]))
            else:
                content_parts.append(record['text'])
        
        if 'data' in record:
            data_obj = record['data']
            data_text = "\n".join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in data_obj.items()])
            content_parts.append(data_text)
        
        if 'leaders' in record:
            leaders_text = "\n".join([f"- {l.get('name', '')}: {l.get('role', '')}" for l in record.get('leaders', [])])
            content_parts.append(f"Leadership:\n{leaders_text}")
        
        if 'testimonials' in record:
            testimonials_text = "\n\n".join([f'"{t.get("quote", "")}" - {t.get("author", "")}' for t in record.get('testimonials', [])])
            content_parts.append(testimonials_text)
        
        content = "\n\n".join(content_parts) if content_parts else title
        
        # Determine source type
        source_type = 'general'
        if 'founder' in section_id or 'leadership' in section_id:
            source_type = 'leadership'
        elif 'vision' in section_id or 'mission' in section_id:
            source_type = 'vision_mission'
        elif 'quick_facts' in section_id or 'overview' in section_id:
            source_type = 'overview'
        
        notices.append(Notice(
            title=title,
            content=content,
            url=record.get('url', 'https://kiit.ac.in/about/'),
            source_type=source_type
        ))
    
    return notices


def main():
    """Main function to load all data"""
    print("Initializing database...")
    init_db()
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(Notice).delete()
        db.query(Course).delete()
        db.commit()
        
        # Load all data
        print("\nLoading placement data...")
        placement_notices = load_placement_data(db)
        db.add_all(placement_notices)
        print(f"✅ Loaded {len(placement_notices)} placement notices")
        
        print("\nLoading courses data...")
        courses = load_courses_data(db)
        db.add_all(courses)
        print(f"✅ Loaded {len(courses)} courses")
        
        print("\nLoading ranking data...")
        ranking_notices = load_ranking_data(db)
        db.add_all(ranking_notices)
        print(f"✅ Loaded {len(ranking_notices)} ranking notices")
        
        print("\nLoading about data...")
        about_notices = load_about_data(db)
        db.add_all(about_notices)
        print(f"✅ Loaded {len(about_notices)} about notices")
        
        db.commit()
        
        # Print summary
        total_notices = db.query(Notice).count()
        total_courses = db.query(Course).count()
        
        print("\n" + "="*50)
        print("✅ Data loading complete!")
        print(f"Total Notices: {total_notices}")
        print(f"Total Courses: {total_courses}")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
