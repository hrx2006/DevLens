DEMO_HTML = """<!DOCTYPE html>
<html>
<head>
    <!-- Intentional SEO Issue: Missing <title> tag -->
    <!-- Intentional SEO Issue: Missing <meta name="description"> tag -->
    <!-- Intentional Performance Issue: Render-blocking script in head -->
    <script src="https://cdn.example.com/library.js"></script>
</head>
<body>
    <h1>Demo Target Web Page</h1>
    <h1>Secondary Duplicate Heading</h1>
    <p>Welcome to the DevLens AI built-in evaluation website target.</p>
    
    <!-- Intentional Accessibility Issue: Image missing alt text -->
    <img src="https://via.placeholder.com/600x400" />
    <img src="https://via.placeholder.com/300x200" alt="" title="Banner image" />
    
    <!-- Intentional Functionality Issue: Form with missing action and password over GET -->
    <form method="GET">
        <label for="user">Username</label>
        <input type="text" id="user" name="username" placeholder="Enter Username" />
        <input type="password" name="password" placeholder="Enter Password" />
        <button type="submit"></button> <!-- Accessibility Issue: Button missing text/label -->
    </form>
    
    <!-- Intentional Accessibility Issue: Generic link text -->
    <p><a href="/more-info">click here</a> to read more details.</p>
    
    <!-- Intentional Functionality Issue: Placeholder anchor link -->
    <p><a href="#">Placeholder Dead Anchor</a></p>
    
    <!-- Intentional Security Issue: Mixed-content image reference on secure page -->
    <img src="http://insecure.example.com/logo.png" alt="Insecure Logo" />

    <!-- Intentional Performance Issue: Multiple unoptimized images without lazy loading -->
    <img src="https://via.placeholder.com/150" />
    <img src="https://via.placeholder.com/150" />
    <img src="https://via.placeholder.com/150" />
    <img src="https://via.placeholder.com/150" />
</body>
</html>
"""

def get_demo_html() -> str:
    return DEMO_HTML
