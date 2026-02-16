const msg = document.getElementById("msg");

async function login(){

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    // validation
    if(!username || !password){
        msg.innerText = "Enter email & password";
        msg.className = "error";
        return;
    }

    msg.innerText = "Checking...";

    try{

        const res = await fetch("/login",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            credentials:"include",   // ⭐⭐⭐ VERY IMPORTANT (AUTO LOGOUT FIX)
            body:JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await res.json();

        if(res.status === 200){

            // OTP page এ ব্যবহারের জন্য email save
            localStorage.setItem("otp_user", username);

            msg.innerText = "OTP sent to email ✔";
            msg.className = "success";

            setTimeout(()=>{
                window.location = "/otp";
            },900);

        }else{
            msg.innerText = data.detail || "Login failed";
            msg.className = "error";
        }

    }catch(err){
        msg.innerText = "Server offline";
        msg.className = "error";
    }
}
