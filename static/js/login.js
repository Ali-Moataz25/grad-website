function login_user(event){
    event.preventDefault();

    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    let role = document.getElementById('role').value;

    fetch('http://127.0.0.1:5001/login_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password,
            role: role
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.result === "success") {
            if (role === "user") {
                window.location.href = "/"; 
            } else if (role === "venue") {
                window.location.href = "/services/venue";
            } else if (role === "hair_dresser") {
                window.location.href = "/services/hairdresser";
            } else if (role === "makeup_artist") {
                window.location.href = "/services/makeupartist";
            } else if (role === "wedding_planner") {
                window.location.href = "/services/weddingplanner";
            } else if (role === "admin") {
                window.location.href = "/";
            } else {
                window.location.href = "/";
            }
        } else {
            alert("Login failed: " + data.result);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Login failed: Network error");
    });
}