const msg=document.getElementById("msg");

async function register(){

    const email=document.getElementById("email").value.trim();
    const password=document.getElementById("password").value.trim();

    if(!email || !password){
        msg.innerText="Fill all fields!";
        msg.className="error";
        return;
    }

    msg.innerText="Creating account...";

    try{

        let res=await fetch("/register",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                email:email,
                password:password
            })
        });

        let data=await res.json();

        if(res.status===200){
            msg.className="success";
            msg.innerText="Account created successfully ✔";

            setTimeout(()=>{
                window.location="/login";
            },1200);

        }else{
            msg.className="error";
            msg.innerText=data.detail;
        }

    }catch{
        msg.className="error";
        msg.innerText="Server error!";
    }
}
