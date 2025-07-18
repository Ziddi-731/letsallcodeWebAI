import streamlit as st
from langchain.tools import StructuredTool
from langchain.agents import AgentExecutor
from langchain.agents.structured_chat.base import StructuredChatAgent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from pathlib import Path
import json
import requests
import random
import base64
import zipfile
import io
import sqlite3
import hashlib
from datetime import datetime

# Initialize SQLite database for user authentication
def init_db():
    conn = sqlite3.connect('store.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                Name text,
                Phone text,
                  email TEXT UNIQUE,
                  password TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# Enhanced futuristic image categories and sources
IMAGE_SOURCES = {
    "hero_backgrounds": [
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80"
    ],
    "portfolio": [
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
    ],
    "team_avatars": [
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
    ],
    "futuristic": [
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
    ],
    "tech": [
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
    ],
    "creative": [
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1677442135136-760c813a743d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
    ]
}

def get_images_for_website(website_type, num_images=6):
    """Get appropriate images based on website type with enhanced selection"""
    images = {
        "hero_bg": random.choice(IMAGE_SOURCES["hero_backgrounds"]),
        "profile": random.choice(IMAGE_SOURCES["team_avatars"]),
        "portfolio": random.sample(IMAGE_SOURCES["portfolio"], min(num_images, len(IMAGE_SOURCES["portfolio"]))),
        "team": random.sample(IMAGE_SOURCES["team_avatars"], min(5, len(IMAGE_SOURCES["team_avatars"]))),
        "features": []
    }
    
    # Enhanced category-specific images
    if website_type.lower() in ["restaurant", "food", "cafe"]:
        images["category"] = random.sample(IMAGE_SOURCES["food"], min(6, len(IMAGE_SOURCES["food"])))
        images["features"] = random.sample(IMAGE_SOURCES["food"], min(3, len(IMAGE_SOURCES["food"])))
    elif website_type.lower() in ["tech", "startup", "saas", "software", "futuristic"]:
        images["category"] = random.sample(IMAGE_SOURCES["futuristic"], min(6, len(IMAGE_SOURCES["futuristic"])))
        images["features"] = random.sample(IMAGE_SOURCES["futuristic"], min(3, len(IMAGE_SOURCES["futuristic"])))
    elif website_type.lower() in ["creative", "agency", "design"]:
        images["category"] = random.sample(IMAGE_SOURCES["creative"], min(6, len(IMAGE_SOURCES["creative"])))
        images["features"] = random.sample(IMAGE_SOURCES["creative"], min(3, len(IMAGE_SOURCES["creative"])))
    else:
        images["category"] = random.sample(IMAGE_SOURCES["futuristic"], min(6, len(IMAGE_SOURCES["futuristic"])))
        images["features"] = random.sample(IMAGE_SOURCES["futuristic"], min(3, len(IMAGE_SOURCES["futuristic"])))
    
    return images

def generate_image_config(website_type: str, description: str) -> str:
    """Generate comprehensive image configuration with usage instructions"""
    images = get_images_for_website(website_type)
    
    config = {
        "hero_bg": images['hero_bg'],
        "profile": images['profile'],
        "portfolio": images['portfolio'],
        "team": images['team'],
        "category": images['category'],
        "features": images['features'],
        "usage": {
            "hero_bg": "Full-width background for header/hero section",
            "profile": "Profile image for about section or team leader",
            "portfolio": "Project/work samples in gallery/portfolio section",
            "team": "Team member photos in about/team section",
            "category": "Content images for services/products sections",
            "features": "Feature highlight images with icons/illustrations"
        }
    }
    
    return json.dumps(config, indent=2)

# API Keys
groq_api_key = "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"
openai_api_key = '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'
gemini_api_key = "AIzaSyDEk75eXsZQRZ2gnkyauHeEW6SOEulnvGk"

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()

def create_user_folder(email):
    """Create a user-specific folder for storing website files"""
    safe_email = email.replace('@', '_').replace('.', '_')
    folder_path = f"user_websites/{safe_email}"
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def create_file(name: str, code: str, user_folder=f"user_websites") -> str:
    """Create a file with given name and code content in user-specific folder"""
    try:
        os.makedirs(user_folder, exist_ok=True)
        
        with open(f"{user_folder}/{name}", 'w', encoding='utf-8') as f:
            f.write(code)
        
        return f"✅ {name} created successfully with {len(code)} characters!"
    except Exception as e:
        return f"❌ Error creating {name}: {str(e)}"

def create_html_file(content, filename="index.html", user_folder=f"user_websites") -> str:
    """Create HTML file with enhanced validation and mobile support"""
    if isinstance(content, dict):
        actual_content = content.get('content', '') or content.get('html', '') or str(content)
    else:
        actual_content = str(content)
    
    # Ensure basic HTML structure if missing
    if "<!DOCTYPE html>" not in actual_content and "<html" not in actual_content:
        actual_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename.replace('.html', '').title()}</title>
    <link rel="stylesheet" href="style.css">
    <!-- Font Awesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    <!-- Animate.css -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
</head>
<body>
{actual_content}
<script src="script.js"></script>
</body>
</html>"""
    
    # Validate the file was created
    result = create_file(filename, actual_content, user_folder)
    if not Path(f"{user_folder}/{filename}").exists():
        raise Exception(f"Failed to create HTML file: {filename}")
    return result

def create_css_file(content, user_folder=f"user_websites") -> str:
    """Create the CSS file with responsive base and mobile menu"""
    if isinstance(content, dict):
        actual_content = content.get('content', '') or content.get('css', '') or str(content)
    else:
        actual_content = str(content)
    
    # Add futuristic base styles if minimal content
    if len(actual_content.strip()) < 100 or ":root" not in actual_content:
        actual_content = f"""/* Futuristic Base Styles */
:root {{
    --primary-color: #6e45e2;
    --secondary-color: #88d3ce;
    --dark-color: #1a1a2e;
    --light-color: #f8f9fa;
    --accent-color: #ff6b6b;
    --glass-color: rgba(255, 255, 255, 0.15);
    --font-main: 'Poppins', sans-serif;
    --font-heading: 'Montserrat', sans-serif;
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: var(--font-main);
    line-height: 1.6;
    color: #fff;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    min-height: 100vh;
}}

/* Glassmorphism Effect */
.glass {{
    background: var(--glass-color);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}}

/* Animations */
@keyframes float {{
    0% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-20px); }}
    100% {{ transform: translateY(0px); }}
}}

.floating {{
    animation: float 6s ease-in-out infinite;
}}

/* Mobile Menu Styles */
.mobile-menu-btn {{
    display: none;
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: white;
    z-index: 1001;
}}

.nav-links {{
    display: flex;
    list-style: none;
}}

/* Responsive Breakpoints */
@media (max-width: 768px) {{
    /* Mobile styles */
    .mobile-menu-btn {{
        display: block;
    }}
    
    .nav-links {{
        display: none;
        flex-direction: column;
        width: 100%;
        position: absolute;
        top: 70px;
        left: 0;
        background: rgba(26, 26, 46, 0.95);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        z-index: 1000;
    }}
    
    .nav-links.active {{
        display: flex;
    }}
    
    .nav-links li {{
        padding: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
}}

@media (min-width: 769px) and (max-width: 1024px) {{
    /* Tablet styles */
}}

{actual_content}"""
    
    # Validate the file was created
    if  Path(f"{user_folder}/style.css").exists():
        with open(f"{user_folder}/style.css",'r') as f:
            pre=f.read()
        actual_content+="\n"+pre

    result = create_file("style.css", actual_content, user_folder)
    if not Path(f"{user_folder}/style.css").exists():
        raise Exception("Failed to create CSS file")
    return result

def create_js_file(content, user_folder=f"user_websites") -> str:
    """Create the JavaScript file with mobile menu functionality"""
    if isinstance(content, dict):
        actual_content = content.get('content', '') or content.get('js', '') or str(content)
    else:
        actual_content = str(content)
    
    # Add futuristic interactions if minimal content
    if len(actual_content.strip()) < 100 or "document.addEventListener" not in actual_content:
        actual_content = f"""// Enhanced Mobile Menu Toggle with Animation
document.addEventListener('DOMContentLoaded', function() {{
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuBtn && navLinks) {{
        menuBtn.addEventListener('click', () => {{
            navLinks.classList.toggle('active');
            menuBtn.innerHTML = navLinks.classList.contains('active') ? 
                '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
        }});
    }}
    
    // Close menu when clicking on a link
    const navItems = document.querySelectorAll('.nav-links a');
    navItems.forEach(item => {{
        item.addEventListener('click', () => {{
            if (window.innerWidth <= 768) {{
                navLinks.classList.remove('active');
                menuBtn.innerHTML = '<i class="fas fa-bars"></i>';
            }}
        }});
    }});
    
    // Scroll animations
    const animateOnScroll = () => {{
        const elements = document.querySelectorAll('.animate-on-scroll');
        elements.forEach(element => {{
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 100) {{
                element.classList.add('animate__animated', 'animate__fadeInUp');
            }}
        }});
    }};
    
    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Run once on load
    
    // Dark mode toggle (optional)
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {{
        darkModeToggle.addEventListener('click', () => {{
            document.body.classList.toggle('light-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('light-mode') ? 'off' : 'on');
        }});
        
        // Check for saved preference
        if (localStorage.getItem('darkMode') === 'off') {{
            document.body.classList.add('light-mode');
        }}
    }}
    
    // Floating animation for elements with .floating class
    const floatingElements = document.querySelectorAll('.floating');
    floatingElements.forEach(el => {{
        el.style.animationDelay = `${{Math.random() * 2}}s`;
    }});
}});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
    anchor.addEventListener('click', function(e) {{
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {{
            window.scrollTo({{
                top: target.offsetTop - 80,
                behavior: 'smooth'
            }});
        }}
    }});
}});

{actual_content}"""
    
    # Validate the file was created
    result = create_file("script.js", actual_content, user_folder)
    if not Path(f"{user_folder}/script.js").exists():
        raise Exception("Failed to create JS file")
    return result

def create_assets_file(filename: str, content: str, user_folder=f"user_websites") -> str:
    """Create additional asset files with validation"""
    try:
        os.makedirs(f"{user_folder}/assets", exist_ok=True)
        with open(f"{user_folder}/assets/{filename}", 'w', encoding='utf-8') as f:
            f.write(content)
        if not Path(f"{user_folder}/assets/{filename}").exists():
            raise Exception(f"Failed to create asset file: {filename}")
        return f"✅ Asset {filename} created successfully!"
    except Exception as e:
        return f"❌ Error creating asset {filename}: {str(e)}"

def create_zip_file(user_folder):
    """Create a zip file of the generated website with validation"""
    try:
        if not os.path.exists(user_folder):
            raise Exception("User folder does not exist")
            
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(user_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, user_folder)
                    zipf.write(file_path, arcname)
        
        memory_file.seek(0)
        return memory_file
    except Exception as e:
        st.error(f"Error creating zip file: {str(e)}")
        return None

def register_user(name,phone,email, password):
    """Register a new user"""
    conn = sqlite3.connect('store.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name,phone,email, password) VALUES (?,?,?, ?)", 
                 (name,phone,email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Email already exists
    finally:
        conn.close()

def authenticate_user(email, password):
    """Authenticate a user"""
    conn = sqlite3.connect('store.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE email = ?", (email,))
    result = c.fetchone()
    conn.close()
    
    if result and verify_password(result[0], password):
        return True
    return False

# Enhanced futuristic structure prompt
structure_prompt = ChatPromptTemplate.from_template("""
You are a world-class futuristic web designer and UX expert. Create a COMPLETE, detailed website structure for: {input}

The website should include appropriate pages based on the website type with FUTURISTIC design elements:
1. **Home Page (index.html)** - Hero section with glassmorphism, animated elements, featured content, call-to-action
2. **About Page (about.html)** - Company/Personal info with floating elements, team with hover effects, mission
3. **Services/Products Page (services.html)** - Detailed offerings with interactive cards (for business sites)
4. **Portfolio/Gallery Page (portfolio.html)** - Work samples/projects with 3D hover effects (for portfolios)
5. **Contact Page (contact.html)** - Contact form with animations, location map, social links
6. **Blog Page (blog.html)** - If applicable, for articles/news with modern cards
7. **Menu Page (menu.html)** - For restaurants/cafes with food animations
8. **Dashboard Page (dashboard.html)** - For SaaS/admin sites with data visualizations

For EACH PAGE, include:
- Complete layout with futuristic header and footer
- Mobile-responsive design with smooth transitions
- Proper navigation between pages with micro-interactions
- Animated content sections
- Image integration with hover effects
- Glassmorphism elements
- Floating animations
- Gradient backgrounds
- Interactive elements with smooth transitions

Also provide:
- Consistent futuristic navigation across all pages
- Animated mobile menu implementation
- Modern color scheme and typography
- Responsive breakpoints with fluid transitions
- Micro-interactions for better UX
""")

# Super detailed coding prompt for complete futuristic frontend
coding_prompt = ChatPromptTemplate.from_template("""
You are a SENIOR FRONTEND DEVELOPER expert in creating complete, multi-page FUTURISTIC websites. 

Based on this comprehensive structure: {input}

And these images: {images}
and save it into given folder in user_websites
Create a COMPLETE, PRODUCTION-READY website with these files:

1. **HTML Files** (use CreateHTMLFile for each):
- Generate all appropriate pages based on website type
- Each page must have complete content with:
  * Glassmorphism elements
  * Animated sections
  * Floating elements
  * Gradient backgrounds
  * Interactive hover effects
- Proper linking between pages with smooth transitions
- Mobile-responsive layout with animated hamburger menu

2. **CSS File** (CreateCSSFile):
- Shared styles for all pages including:
  * Glassmorphism styles
  * Animation keyframes
  * Gradient backgrounds
  * Modern typography
  * Responsive grid system
- Mobile-first responsive design with:
  * Animated mobile menu
  * Fluid transitions between breakpoints
- Consistent futuristic styling across pages

3. **JavaScript File** (CreateJSFile):
- Enhanced mobile menu functionality with animations
- Smooth scrolling with parallax effects
- Form validation with interactive feedback
- Scroll-triggered animations
- Interactive elements with micro-interactions
- Floating element animations
- Dark/light mode toggle (if applicable)

IMPORTANT REQUIREMENTS:
1. FUTURISTIC DESIGN:
- Glassmorphism effects
- Animated elements
- Floating components
- Gradient backgrounds
- Micro-interactions
- Smooth transitions

2. MOBILE RESPONSIVENESS:
- Animated hamburger menu for mobile
- Responsive images and layouts
- Proper viewport meta tag
- Touch-friendly interactions

3. MULTI-PAGE STRUCTURE:
- Consistent header/navigation across pages
- Proper linking between pages with smooth transitions
- Each page must be complete with content

4. IMAGE USAGE:
- Use provided images appropriately
- Include hover effects on images
- Add proper alt text
- Optimize for performance

Generate ALL files using the provided tools. Make sure to:
1. Create all HTML pages first (index.html, about.html, etc.)
2. Then create the shared CSS file (style.css)
3. Finally create the shared JS file (script.js)
4. Validate all files were created successfully
""")

# Initialize LLMs with higher temperature for creativity
structure_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7, google_api_key=gemini_api_key)
coding_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7, google_api_key=gemini_api_key)

# Create chains
output_parser = StrOutputParser()
structure_chain = structure_prompt | structure_llm | output_parser

# Enhanced tools with better descriptions and validation
tools = [
    StructuredTool.from_function(
        name="CreateHTMLFile",
        func=create_html_file,
        description="""Create an HTML file with FUTURISTIC elements. 
        Input: (content: str, filename: str, user_folder: str)
        - content: Complete HTML code as string with glassmorphism, animations
        - filename: Name of file (e.g., 'index.html', 'about.html')
        - user_folder: User-specific folder to store files
        Creates semantic HTML5 with:
        - Mobile-responsive structure
        - Linked CSS/JS files
        - Glassmorphism elements
        - Animated components
        - Proper navigation
        - Image integration with hover effects
        save it into given folder in user_websites"""
    ),
    StructuredTool.from_function(
        name="CreateCSSFile", 
        func=create_css_file,
        description="""Create the shared CSS file (style.css) with futuristic styles.
        Input: (content: str, user_folder: str)
        - content: Complete CSS code as string with animations, glassmorphism
        - user_folder: User-specific folder to store files
        Includes:
        - Glassmorphism effects
        - Animation keyframes
        - Mobile-first responsive design
        - Navigation styling with animations
        - Gradient backgrounds
        - Modern design elements
        save it into given folder in user_websites"""
    ),
    StructuredTool.from_function(
        name="CreateJSFile",
        func=create_js_file,
        description="""Create the shared JavaScript file (script.js) with interactions.
        Input: (content: str, user_folder: str)
        - content: Complete JS code as string with animations, interactions
        - user_folder: User-specific folder to store files
        Includes:
        - Animated mobile menu functionality
        - Smooth scrolling with parallax
        - Form validation with feedback
        - Scroll-triggered animations
        - Interactive elements
        - Floating animations
        save it into given folder in user_websites"""
    ),
    StructuredTool.from_function(
        name="GenerateImageConfig",
        func=generate_image_config,
        description="""Generate image configuration for the website.
        Input: website_type (string), description (string).
        Returns JSON with curated image URLs and usage instructions.save it into given folder in user_websites"""
    ),
    StructuredTool.from_function(
        name="CreateAssetsFile",
        func=create_assets_file,
        description="""Create additional asset files.
        Input: (filename: str, content: str, user_folder: str)
        - filename: Name of the asset file
        - content: Content of the asset file
        - user_folder: User-specific folder to store files
        Use for additional CSS, JS, or configuration files.save it into given folder in user_websites"""
    )
]

# Create agent with enhanced configuration
agent = StructuredChatAgent.from_llm_and_tools(
    tools=tools,
    llm=coding_llm,
    prompt=coding_prompt,
    verbose=True
)

code_writer = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=15,  # Increased for complex futuristic design
    return_intermediate_steps=True
)

# Streamlit Interface
st.set_page_config(
    page_title="AI Futuristic Website Generator",
    page_icon="🚀",
    layout="wide"
)

# Authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'user_folder' not in st.session_state:
    st.session_state.user_folder = None

# Authentication functions
def show_login():   
    with st.form("Login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if authenticate_user(email, password):
                st.session_state.authenticated = True
                st.session_state.user_email = email
                conn = sqlite3.connect('store.db')
                c = conn.cursor()
                c.execute("Select name from users where email =?",(email,))
                r=c.fetchone()
                st.session_state.user_name=r[0]
                st.session_state.user_folder = create_user_folder(email)
                st.rerun()
            else:
                st.error("Invalid email or password")

def show_register():
    with st.form("Register"):
        name=st.text_input("Name")
        phone=st.text_input("Phone Number")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if password != confirm_password:
                st.error("Passwords don't match")
            else:
                if register_user(name,phone,email, password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Email already registered")

def show_about():
    st.markdown("""
    ## About Us
    
    Our team **LetsAllCode** created this AI-powered website generator to help people quickly create professional, 
    responsive websites without coding knowledge.
    
    **Our Mission:**
    - Democratize web development
    - Provide high-quality, production-ready websites
    - Make the web more accessible to everyone
    
    **Our CEO:** Zohaib Shabbir \n 
    **Contact us at:** zohaibshabbir988@gmail.com\n
    **Instagram : ** https://www.instagram.com/letsall.code\n
    **Linkdin : ** www.linkedin.com/in/zohaib-shabbir-508427297\n
    This tool generates complete frontend solutions with:
    - Multiple pages
    - Mobile-responsive design
    - Modern UI/UX
    - Interactive elements
    """)

# Show authentication or main app
if not st.session_state.authenticated:
    st.title("AI Futuristic Website Generator")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "About"])
    
    with tab1:
        show_login()
    
    with tab2:
        show_register()
    
    with tab3:
        show_about()
else:
    # Main app interface for authenticated users
    st.title(f"🚀 Letsallcode AI Professional Website Generator (Welcome {st.session_state.user_name})")
    st.markdown("### Create complete, responsive multi-page websites with mobile-friendly navigation!")
    
    # Enhanced sidebar configuration
    with st.sidebar:
        st.header("⚙️ Futuristic Website Configuration")
        
        website_type = st.selectbox(
            "Website Type",
            ["Portfolio", "Business", "Landing Page", "Blog", "E-commerce", 
             "Restaurant", "Agency", "SaaS", "Startup", "Creative Agency", "Futuristic", "Custom"],
            index=0
        )
        
        design_style = st.selectbox(
            "Design Style", 
            ["Glassmorphism", "Neumorphism", "Cyberpunk", "Holographic", 
             "Dark Futuristic", "Light Futuristic", "Gradient Mesh"],
            index=0
        )
        mobile_menu_style = st.selectbox(
        "Mobile Menu Style",
        ["Hamburger Menu", "Full-screen Overlay", "Slide-in Panel"],
        index=0
    )
        st.markdown("---")
        st.markdown("**Animation Settings**")
        animation_intensity = st.select_slider(
            "Animation Intensity",
            options=["Subtle", "Moderate", "High", "Extreme"],
            value="Moderate"
        )
        
        st.markdown("---")
        st.markdown("**Special Features**")
        special_features = st.multiselect(
            "Select Features",
            ["Glassmorphism", "Parallax Effects", "3D Elements", "Particle Backgrounds",
             "Animated Gradients", "Dark Mode Toggle", "Micro-interactions"],
            default=["Glassmorphism", "Animated Gradients", "Micro-interactions"]
        )
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.rerun()

    # Main input area
    col1, col2 = st.columns([2, 1])

    with col1:
        input_text = st.text_area(
            "✍️ Describe your website in detail:", 
            placeholder="""Example: Create a business website for a digital marketing agency called 'Pixel Perfect'.

Key requirements:
- Modern, clean design with blue color scheme
- Mobile-friendly with hamburger menu
- Animations on scroll
- Testimonials section on homepage
- Client logos showcase""",
            height=200
        )

    with col2:
        st.info("💡 **Tips for better results:**")
        st.markdown("""
        - Describe your business/purpose
        - Mention specific features needed
        - Include color preferences
        - Specify any special requirements
        - Add branding elements if any
        """)

    # Enhanced input with all configurations
    enhanced_input = f"""
    WEBSITE TYPE: {website_type}
    DESIGN STYLE: {design_style}
    MOBILE MENU STYLE: {mobile_menu_style}
    ANIMATION INTENSITY :{animation_intensity}
    SPECIAL FEATURES: {', '.join(special_features)}
    FOLDER : /user_websites/{st.session_state.user_email.replace("@","_").replace(".","_")}
    DETAILED DESCRIPTION:
    {input_text}

    REQUIREMENTS:
    - Create COMPLETE multi-page website
    - All pages must be properly linked
    - Mobile-responsive design
    - {mobile_menu_style} for small screens
    - Modern, professional appearance
    - Include all specified features
    - Use images appropriately
    use only style.css for css not anyother path like "css/style.css"
    use  js file script.js not anyother path like "js/script.js"
    use images from links instead folder like "images/"
    make it responsive for both desktop,mobile and tablets
    """

    # Generation button
    if st.button("🎨 Generate Complete Website", type="primary", use_container_width=True):
        if input_text:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Generate comprehensive structure
                status_text.text("🔄 Planning comprehensive website structure...")
                progress_bar.progress(20)
                
                structure_response = structure_chain.invoke({"input": enhanced_input})
                
                progress_bar.progress(40)
                status_text.text("✅ Website structure planned!")
                
                with st.expander("📋 View Complete Website Structure", expanded=True):
                    st.markdown(structure_response)
                
                # Step 2: Get images for website
                status_text.text("🖼️ Curating images for website...")
                progress_bar.progress(50)
                
                image_config = generate_image_config(website_type, input_text)
                images = json.loads(image_config)
                
                with st.expander("📸 View Image Configuration", expanded=False):
                    st.json(images)
                
                # Step 3: Generate complete code
                status_text.text("💻 Generating complete professional code...")
                progress_bar.progress(70)
                
                code_response = code_writer.invoke({
                    "input": structure_response,
                    "images": image_config,
                    "user_folder": st.session_state.user_folder
                })
                
                progress_bar.progress(100)
                status_text.text("🎉 Complete website generated successfully!")
                
                # Display results
                st.success("🎉 **Complete Multi-Page Website Generated Successfully!**")
                
                # Create download zip button

                zip_file = create_zip_file(st.session_state.user_folder)
                if zip_file:
                    st.download_button(
                        label="📥 Download Website as ZIP",
                        data=zip_file,
                        file_name=f"{st.session_state.user_email}_website.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                
                # Display file previews
                tab1, tab2, tab3 = st.tabs(["HTML Files", "CSS Preview", "JS Preview"])
                
                with tab1:
                    if Path(st.session_state.user_folder).exists():
                        html_files = list(Path(st.session_state.user_folder).glob("*.html"))
                        if html_files:
                            st.success("📄 **Generated HTML Pages:**")
                            for file in html_files:
                                with open(file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                with st.expander(f"View {file.name}", expanded=False):
                                    st.code(content[:1000] + "..." if len(content) > 1000 else content, language="html")
                        else:
                            st.warning("No HTML files found")
                    else:
                        st.warning("User folder not found")
                
                with tab2:
                    css_file = Path(f"{st.session_state.user_folder}/style.css")
                    if css_file.exists():
                        with open(css_file, 'r', encoding='utf-8') as f:
                            css_content = f.read()
                        st.code(css_content[:2000] + "..." if len(css_content) > 2000 else css_content, language="css")
                    else:
                        st.warning("CSS file not found")
                
                with tab3:
                    js_file = Path(f"{st.session_state.user_folder}/script.js")
                    if js_file.exists():
                        with open(js_file, 'r', encoding='utf-8') as f:
                            js_content = f.read()
                        st.code(js_content[:2000] + "..." if len(js_content) > 2000 else js_content, language="javascript")
                    else:
                        st.warning("JS file not found")
                
                # Show live preview of homepage
                index_file = Path(f"{st.session_state.user_folder}/index.html")
                if index_file.exists():
                    st.markdown("---")
                    st.markdown("### 🌐 Home Page Preview")
                    
                    # Read HTML file
                    with open(index_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Display in iframe
                    st.components.v1.html(html_content, height=600, scrolling=True)
                
            except Exception as e:
                st.error(f"❌ **Error generating website:** {str(e)}")
                st.info("💡 **Troubleshooting:**")
                st.markdown("""
                - Check your internet connection
                - Verify API keys are working
                - Try simplifying your description
                - Ensure all required fields are filled
                """)
        else:
            st.warning("⚠️ **Please enter a detailed description for your website**")

    # Additional features section
    st.markdown("---")
    st.markdown("### 🛠️ Additional Tools")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📂 View Files", use_container_width=True):
            try:
                files = list(Path(st.session_state.user_folder).glob("*"))
                if files:
                    st.success("📁 **Generated Files:**")
                    for file in files:
                        file_size = file.stat().st_size / 1024  # in KB
                        st.write(f"📄 {file.name} ({file_size:.1f} KB)")
                else:
                    st.info("No files generated yet")
            except:
                st.info("User folder not found")

    with col2:
        if st.button("🗑️ Clear Files", use_container_width=True):
            try:
                import shutil
                if Path(st.session_state.user_folder).exists():
                    shutil.rmtree(st.session_state.user_folder)
                    st.success("All files cleared!")
                else:
                    st.info("No files to clear")
            except Exception as e:
                st.error(f"Error: {e}")

    with col3:
        if st.button("🚀 Deploy Tips", use_container_width=True):
            st.info("🚀 **Deployment Options:**")
            st.markdown("""
            - **Netlify**: Drag & drop deployment
            - **Vercel**: Git-based deployment
            - **GitHub Pages**: Free hosting
            - **Firebase**: Google hosting
            - **AWS S3**: Scalable hosting
            """)

    # About section for authenticated users
    st.markdown("---")
    show_about()
