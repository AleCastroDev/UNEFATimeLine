const baseRemPorcentual = 3.883;

const setRem = () => {
    const vw = window.innerWidth;
    const rem = (baseRemPorcentual / 100) * vw;
    document.documentElement.style.fontSize = `${rem}px`;
}

window.addEventListener("resize", setRem);
setRem()