function register(event) {
    event.preventDefault();

    let select_value = document.getElementById('role').value;

    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;

   let formData = new FormData();
    formData.append('select_value', select_value);
    formData.append('username', username);
    formData.append('password', password);
    formData.append('phone_number', document.getElementById('phone_number').value);

if (select_value === "user" || select_value === "admin") {
    formData.append('email', document.getElementById('email').value);
} else {
    if (document.getElementById('description'))
        formData.append('description', document.getElementById('description').value);
    if (document.getElementById('location'))
        formData.append('location', document.getElementById('location').value);
    if (document.getElementById('price'))
        formData.append('price', document.getElementById('price').value);
    if (document.getElementById('media').files[0])
        formData.append('media', document.getElementById('media').files[0]);
}

fetch('http://127.0.0.1:5001/register_user', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success || data.type) {
        alert("Thank you for registering.\nRedirecting to login page.");
        window.location.href = "/login";
    } else {
        alert("Registration failed: " + (data.message || "Unknown error"));
    }
})
.catch(error => {
    alert("Error during registration: " + error);
});
}


function register_type(){
    let select_value= document.getElementById('role').value
    let form_element = document.getElementById('registerHolder')
    console.log(select_value)
    if (select_value=== "venue" ){
        form_element.innerHTML = ""
        let description = document.createElement('label')
        let description_input = document.createElement('input')
        description_input.id="description"
        description.innerText= "Description"

        let phone_number  = document.createElement('label')
        let phone_number_input = document.createElement('input')
        phone_number_input.id="phone_number"
        phone_number.innerText= "Phone Number"

        let location  = document.createElement('label')
        let location_input = document.createElement('input')
        location_input.id="location"
        location.innerText= "Location"

        let price  = document.createElement('label')
        let price_input = document.createElement('input')
        price_input.id="price"
        price.innerText= "Price per day"


        let media  = document.createElement('label')
        let media_input = document.createElement('input')
        media_input.type="file"
        media_input.id="media"
        media.innerText= "Media"




        form_element.appendChild(description)
        form_element.appendChild(description_input)

        form_element.appendChild(phone_number)
        form_element.appendChild(phone_number_input)
        
        form_element.appendChild(location)
        form_element.appendChild(location_input)

        form_element.appendChild(price)
        form_element.appendChild(price_input)
          
        form_element.appendChild(media)
        form_element.appendChild(media_input)

        
        


    }
    else if(select_value==="user"){
        form_element.innerHTML = ""
        let phone_number  = document.createElement('label')
        let phone_number_input = document.createElement('input')
        phone_number_input.id="phone_number"
        phone_number.innerText= "Phone Number"

        let email  = document.createElement('label')
        let email_input = document.createElement('input')
        email_input.id="email"
        email.innerText= "Email"



        form_element.appendChild(phone_number)
        form_element.appendChild(phone_number_input)

        form_element.appendChild(email)
        form_element.appendChild(email_input)


    }

    else if(select_value==="admin"){
        form_element.innerHTML = ""
        let phone_number  = document.createElement('label')
        let phone_number_input = document.createElement('input')
        phone_number_input.id="phone_number"
        phone_number.innerText= "Phone Number"

        let email  = document.createElement('label')
        let email_input = document.createElement('input')
        email_input.id="email"
        email.innerText= "Email"



        form_element.appendChild(phone_number)
        form_element.appendChild(phone_number_input)

        form_element.appendChild(email)
        form_element.appendChild(email_input)


    }


    else if (select_value=== "hair_dresser" ){
        form_element.innerHTML = ""
        let description = document.createElement('label')
        let description_input = document.createElement('input')
        description_input.id="description"
        description.innerText= "Description"

        let phone_number  = document.createElement('label')
        let phone_number_input = document.createElement('input')
        phone_number_input.id="phone_number"
        phone_number.innerText= "Phone Number"

        let location  = document.createElement('label')
        let location_input = document.createElement('input')
        location_input.id="location"
        location.innerText= "Location"

        let price  = document.createElement('label')
        let price_input = document.createElement('input')
        price_input.id="price"
        price.innerText= "Price per hour"


        let media  = document.createElement('label')
        let media_input = document.createElement('input')
        media_input.type="file"
        media_input.id="media"
        media.innerText= "Media"




        form_element.appendChild(description)
        form_element.appendChild(description_input)

        form_element.appendChild(phone_number)
        form_element.appendChild(phone_number_input)
        
        form_element.appendChild(location)
        form_element.appendChild(location_input)

        form_element.appendChild(price)
        form_element.appendChild(price_input)
          
        form_element.appendChild(media)
        form_element.appendChild(media_input)

        
        


    }
    
    else if (select_value=== "wedding_planner" ){
        form_element.innerHTML = ""
        let description = document.createElement('label')
        let description_input = document.createElement('input')
        description_input.id="description"
        description.innerText= "Description"

        let phone_number  = document.createElement('label')
        let phone_number_input = document.createElement('input')
        phone_number_input.id="phone_number"
        phone_number.innerText= "Phone Number"

        let price  = document.createElement('label')
        let price_input = document.createElement('input')
        price_input.id="price"
        price.innerText= "Price per event"


        let media  = document.createElement('label')
        let media_input = document.createElement('input')
        media_input.type="file"
        media_input.id="media"
        media.innerText= "Media"




        form_element.appendChild(description)
        form_element.appendChild(description_input)

        form_element.appendChild(phone_number)
        form_element.appendChild(phone_number_input)
        
        form_element.appendChild(price)
        form_element.appendChild(price_input)
          
        form_element.appendChild(media)
        form_element.appendChild(media_input)

        
        


    }

    
    else if (select_value=== "makeup_artist" ){
        form_element.innerHTML = ""
        let description = document.createElement('label')
        let description_input = document.createElement('input')
        description_input.id="description"
        description.innerText= "Description"

        let phone_number  = document.createElement('label')
        let phone_number_input = document.createElement('input')
        phone_number_input.id="phone_number"
        phone_number.innerText= "Phone Number"

        let location  = document.createElement('label')
        let location_input = document.createElement('input')
        location_input.id="location"
        location.innerText= "Location"

        let price  = document.createElement('label')
        let price_input = document.createElement('input')
        price_input.id="price"
        price.innerText= "Price per hour"


        let media  = document.createElement('label')
        let media_input = document.createElement('input')
        media_input.type="file"
        media_input.id="media"
        media.innerText= "Media"




        form_element.appendChild(description)
        form_element.appendChild(description_input)

        form_element.appendChild(phone_number)
        form_element.appendChild(phone_number_input)
        
        form_element.appendChild(location)
        form_element.appendChild(location_input)

        form_element.appendChild(price)
        form_element.appendChild(price_input)
          
        form_element.appendChild(media)
        form_element.appendChild(media_input)

        
        


    }
}