console.log("hola desde main js ")
const copyBtn = [...document.getElementsByClassName('copy-btn')]

copyBtn.forEach(btn=> btn.addEventListener('click', ()=>{
    const project = btn.getAttribute('data-project')
    navigator.clipboard.writeText(project)
    btn.textContent = 'Copied'
}))

// Actualiza precio total cada que cambia un campo

// Calcula suscripción
const botonCalculaSubscription = document.getElementById('btnCalculaSub')
botonCalculaSubscription.addEventListener('click', () =>{
    var form = new FormData(document.getElementById('subscription-form'))
    fetch("/", {
        method: "POST", 
        body: form,
        headers: {
            "X-CSRFToken": getCookie('csrftoken')
        }
    }).then(function(response){
        console.log(response)
    })
})
const n_trees = document.getElementById('id_n_trees')
const totalField = document.getElementById('id_total_price')
const unit_price = 0
n_trees.addEventListener('change', function (evt) {
    total = this.value * unit_price
    totalField.setAttribute('value',total);
});

// funcion para el token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}