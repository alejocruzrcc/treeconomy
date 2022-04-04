console.log("hola desde main js ")
const copyBtn = [...document.getElementsByClassName('copy-btn')]

copyBtn.forEach(btn=> btn.addEventListener('click', ()=>{
    const project = btn.getAttribute('data-project')
    navigator.clipboard.writeText(project)
    btn.textContent = 'Copied'
}))