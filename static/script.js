// LOGIN
function validateLogin(){
let u=document.getElementById("username").value.trim();
let p=document.getElementById("password").value.trim();

if(u.length<3){alert("Username too short");return false;}
if(p.length<4){alert("Password too short");return false;}

return true;
}

// REGISTER
function validateRegister(){
let p=document.getElementById("password").value.trim();

if(p.length<6){
alert("Password must be 6+ characters");
return false;
}

return true;
}

// PROBLEM
function validateProblem(){
let t=document.getElementById("title").value.trim();
let d=document.getElementById("description").value.trim();

if(t.length<5){alert("Title too short");return false;}
if(d.length<10){alert("Description too short");return false;}

return true;
}

// TESTCASE
function validateTestcase(){
let i=document.getElementById("input").value.trim();
let o=document.getElementById("expected_output").value.trim();

if(i==""||o==""){alert("Fields cannot be empty");return false;}

return true;
}

// CODE
function validateCode(){
if(!window.editor) return true;

let code=editor.getValue().trim();

if(code.length<5){
alert("Code cannot be empty");
return false;
}

return true;
}

/* ===== EXAM MODE ===== */
document.addEventListener("contextmenu",e=>e.preventDefault());
document.addEventListener("copy",e=>e.preventDefault());
document.addEventListener("paste",e=>e.preventDefault());

document.addEventListener("visibilitychange",function(){
if(document.hidden){
alert("Tab switching detected!");
}
});