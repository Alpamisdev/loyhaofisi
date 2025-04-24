import sqlite3
import os
import datetime
import random

def add_sample_data():
    """Add sample data to the database for testing and demonstration purposes."""
    # Connect to SQLite database
    db_path = os.environ.get('DATABASE_PATH', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Current timestamp for created_at fields
    now = datetime.datetime.now().isoformat()
    
    # Check if database is initialized
    try:
        c.execute("SELECT COUNT(*) FROM admin_users")
    except sqlite3.OperationalError:
        print("Error: Database not initialized. Please run init_db.py first.")
        return

    print("Adding sample data to the database...")

    # ===================== MENU =====================
    menu_items = [
        ("Home", "home"),
        ("About Us", "info-circle"),
        ("Services", "briefcase"),
        ("Blog", "book-open"),
        ("Contact", "mail")
    ]
    
    for name, icon in menu_items:
        c.execute("INSERT INTO menu (name, icon) VALUES (?, ?)", (name, icon))
    
    print("Added menu items")

    # ===================== YEAR NAME =====================
    year_names = [
        ("Year of Innovation", "innovation.jpg"),
        ("Year of Digital Transformation", "digital.jpg")
    ]
    
    for text, img in year_names:
        c.execute("INSERT INTO year_name (text, img) VALUES (?, ?)", (text, img))
    
    print("Added year names")

    # ===================== CONTACTS =====================
    contacts = {
        "address": "123 Main Street, Tashkent, Uzbekistan",
        "phone_number": "+998 71 123 4567",
        "email": "info@loyha.uz"
    }
    
    c.execute(
        "INSERT INTO contacts (address, phone_number, email) VALUES (?, ?, ?)",
        (contacts["address"], contacts["phone_number"], contacts["email"])
    )
    
    print("Added contacts")

    # ===================== SOCIAL NETWORKS =====================
    social_networks = [
        ("Facebook", "facebook", "https://facebook.com/loyha"),
        ("Instagram", "instagram", "https://instagram.com/loyha"),
        ("Telegram", "send", "https://t.me/loyha"),
        ("LinkedIn", "linkedin", "https://linkedin.com/company/loyha")
    ]
    
    for name, icon, link in social_networks:
        c.execute(
            "INSERT INTO social_networks (name, icon, link) VALUES (?, ?, ?)",
            (name, icon, link)
        )
    
    print("Added social networks")

    # ===================== FEEDBACK =====================
    feedback_themes = ["General Inquiry", "Technical Support", "Partnership", "Job Application", "Suggestion"]
    
    feedback_items = [
        ("John Doe", "+998 90 123 4567", "john@example.com", "General Inquiry", "I'm interested in your services. Please contact me for more information."),
        ("Jane Smith", "+998 91 234 5678", "jane@example.com", "Technical Support", "I'm having trouble accessing my account. Can you help?"),
        ("Bob Johnson", "+998 93 345 6789", "bob@example.com", "Partnership", "Our company would like to discuss a potential partnership."),
        ("Alice Brown", "+998 94 456 7890", "alice@example.com", "Job Application", "I'm interested in the developer position advertised on your website."),
        ("David Wilson", "+998 95 567 8901", "david@example.com", "Suggestion", "I have a suggestion for improving your website navigation.")
    ]
    
    for full_name, phone_number, email, theme, text in feedback_items:
        timestamp = (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))).isoformat()
        c.execute(
            "INSERT INTO feedback (full_name, phone_number, email, theme, text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (full_name, phone_number, email, theme, text, timestamp)
        )
    
    print("Added feedback items")

    # ===================== STAFF =====================
    staff_members = [
        ("CEO", "Alisher Usmanov", "alisher@loyha.uz", "+998 71 123 4567", "alisher.jpg"),
        ("CTO", "Dilshod Karimov", "dilshod@loyha.uz", "+998 71 123 4568", "dilshod.jpg"),
        ("Marketing Director", "Nodira Azimova", "nodira@loyha.uz", "+998 71 123 4569", "nodira.jpg"),
        ("Lead Developer", "Timur Rakhimov", "timur@loyha.uz", "+998 71 123 4570", "timur.jpg"),
        ("UI/UX Designer", "Kamila Yusupova", "kamila@loyha.uz", "+998 71 123 4571", "kamila.jpg")
    ]
    
    for position, full_name, email, phone, photo in staff_members:
        c.execute(
            "INSERT INTO staff (position, full_name, email, phone, photo) VALUES (?, ?, ?, ?, ?)",
            (position, full_name, email, phone, photo)
        )
    
    print("Added staff members")

    # ===================== BLOG =====================
    blog_categories = [
        "Technology",
        "Business",
        "Design",
        "Development",
        "Industry News"
    ]
    
    for name in blog_categories:
        c.execute("INSERT INTO blog_categories (name) VALUES (?)", (name,))
    
    # Get the inserted category IDs
    c.execute("SELECT id FROM blog_categories")
    category_ids = [row['id'] for row in c.fetchall()]
    
    blog_items = [
        (category_ids[0], "The Future of Web Development", "web-future.jpg", 
         "Web development is constantly evolving. Here's what to expect in the coming years.", 
         "In this article, we explore the emerging trends in web development and how they will shape the future of the industry."),
        
        (category_ids[1], "Business Strategies for Tech Startups", "startup.jpg", 
         "Effective strategies for tech startups to grow and succeed in a competitive market.", 
         "Starting a tech company is challenging. This article provides practical advice for entrepreneurs looking to make their mark."),
        
        (category_ids[2], "Principles of Modern UI Design", "ui-design.jpg", 
         "Key principles that guide effective and user-friendly interface design.", 
         "Good UI design is essential for user engagement. Learn the fundamental principles that make interfaces intuitive and appealing."),
        
        (category_ids[3], "Introduction to Microservices Architecture", "microservices.jpg", 
         "Understanding the basics of microservices and how they differ from monolithic architectures.", 
         "Microservices are changing how we build applications. This article introduces the concept and its benefits."),
        
        (category_ids[4], "Latest Developments in AI and Machine Learning", "ai-ml.jpg", 
         "Recent breakthroughs in artificial intelligence and their implications for various industries.", 
         "AI continues to advance at a rapid pace. Stay updated with the latest developments and their potential impact.")
    ]
    
    for category_id, title, img, intro_text, text in blog_items:
        timestamp = (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 60))).isoformat()
        views = random.randint(10, 500)
        c.execute(
            """INSERT INTO blog_items 
               (category_id, title, img_or_video_link, date_time, views, text, intro_text) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (category_id, title, img, timestamp, views, text, intro_text)
        )
    
    print("Added blog categories and items")

    # ===================== ABOUT COMPANY =====================
    about_company = {
        "title": "About Loyha.uz",
        "img": "company.jpg",
        "text": """
        Loyha.uz is a leading technology company in Uzbekistan, specializing in web development, 
        mobile applications, and digital transformation services. Founded in 2015, we have grown 
        to become a trusted partner for businesses seeking innovative digital solutions.
        
        Our team of experienced professionals is dedicated to delivering high-quality products 
        that meet the unique needs of our clients. We combine technical expertise with creative 
        thinking to solve complex problems and create exceptional user experiences.
        
        At Loyha.uz, we believe in continuous learning and staying at the forefront of technological 
        advancements. This commitment to excellence has allowed us to build long-lasting relationships 
        with our clients and establish ourselves as industry leaders.
        """
    }
    
    timestamp = (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))).isoformat()
    views = random.randint(100, 1000)
    
    c.execute(
        "INSERT INTO about_company (title, img, date_time, views, text) VALUES (?, ?, ?, ?, ?)",
        (about_company["title"], about_company["img"], timestamp, views, about_company["text"])
    )
    
    # About company categories
    about_company_categories = [
        "Our Mission",
        "Our Vision",
        "Our Values",
        "Our History",
        "Our Team"
    ]
    
    for name in about_company_categories:
        c.execute("INSERT INTO about_company_categories (name) VALUES (?)", (name,))
    
    # Get the inserted category IDs
    c.execute("SELECT id FROM about_company_categories")
    about_category_ids = [row['id'] for row in c.fetchall()]
    
    # About company category items
    about_company_items = [
        (about_category_ids[0], "Our Mission", 
         "Our mission is to empower businesses through innovative digital solutions that drive growth and success."),
        
        (about_category_ids[1], "Our Vision", 
         "We envision a future where technology enhances every aspect of business and daily life, making processes more efficient and experiences more enjoyable."),
        
        (about_category_ids[2], "Excellence", 
         "We strive for excellence in everything we do, from code quality to customer service."),
        
        (about_category_ids[2], "Innovation", 
         "We embrace innovation and continuously explore new technologies and approaches."),
        
        (about_category_ids[2], "Integrity", 
         "We conduct our business with integrity, honesty, and transparency."),
        
        (about_category_ids[3], "The Beginning", 
         "Loyha.uz was founded in 2015 by a group of passionate developers with a vision to transform the digital landscape in Uzbekistan."),
        
        (about_category_ids[3], "Growth and Expansion", 
         "By 2018, we had expanded our team to 20 professionals and moved to a larger office space to accommodate our growing operations."),
        
        (about_category_ids[4], "Leadership", 
         "Our leadership team brings decades of combined experience in technology, business, and design.")
    ]
    
    for category_id, title, text in about_company_items:
        timestamp = (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 45))).isoformat()
        views = random.randint(50, 300)
        
        # For some items, associate with feedback
        feedback_id = None
        if random.random() > 0.7:  # 30% chance to have associated feedback
            c.execute("SELECT id FROM feedback ORDER BY RANDOM() LIMIT 1")
            feedback_row = c.fetchone()
            if feedback_row:
                feedback_id = feedback_row['id']
        
        c.execute(
            """INSERT INTO about_company_category_items 
               (category_id, title, text, views, date_time, feedback_id) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (category_id, title, text, views, timestamp, feedback_id)
        )
    
    print("Added about company information")

    # ===================== DOCUMENTS =====================
    document_categories = [
        "Policies",
        "Guidelines",
        "Templates",
        "Reports",
        "Presentations"
    ]
    
    for name in document_categories:
        c.execute("INSERT INTO documents_categories (name) VALUES (?)", (name,))
    
    # Get the inserted category IDs
    c.execute("SELECT id FROM documents_categories")
    doc_category_ids = [row['id'] for row in c.fetchall()]
    
    documents = [
        (doc_category_ids[0], "Privacy Policy", "Privacy Policy", "privacy-policy.pdf"),
        (doc_category_ids[0], "Terms of Service", "Terms of Service", "terms-of-service.pdf"),
        (doc_category_ids[0], "Cookie Policy", "Cookie Policy", "cookie-policy.pdf"),
        
        (doc_category_ids[1], "Brand Guidelines", "Brand Guidelines", "brand-guidelines.pdf"),
        (doc_category_ids[1], "Development Standards", "Development Standards", "dev-standards.pdf"),
        
        (doc_category_ids[2], "Project Proposal Template", "Project Proposal", "project-proposal-template.docx"),
        (doc_category_ids[2], "Invoice Template", "Invoice", "invoice-template.xlsx"),
        
        (doc_category_ids[3], "Annual Report 2022", "Annual Report 2022", "annual-report-2022.pdf"),
        (doc_category_ids[3], "Q1 2023 Performance", "Q1 2023 Report", "q1-2023-report.pdf"),
        
        (doc_category_ids[4], "Company Overview", "Company Overview", "company-overview.pptx"),
        (doc_category_ids[4], "Service Offerings", "Service Offerings", "service-offerings.pptx")
    ]
    
    for category_id, title, name, link in documents:
        c.execute(
            "INSERT INTO documents_items (category_id, title, name, link) VALUES (?, ?, ?, ?)",
            (category_id, title, name, link)
        )
    
    print("Added document categories and items")

    # ===================== MENU LINKS =====================
    # Link menu items to content
    menu_links = [
        (1, "home", None, "Home", 1),  # Home
        (2, "about", None, "About Us", 2),  # About Us
        (3, "services", None, "Services", 3),  # Services
        (4, "blog", None, "Blog", 4),  # Blog
        (5, "contact", None, "Contact", 5)  # Contact
    ]
    
    for menu_id, target_type, target_id, label, position in menu_links:
        c.execute(
            """INSERT INTO menu_links 
               (menu_id, target_type, target_id, label, position) 
               VALUES (?, ?, ?, ?, ?)""",
            (menu_id, target_type, target_id, label, position)
        )
    
    print("Added menu links")

    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Sample data added successfully!")

if __name__ == "__main__":
    add_sample_data()
