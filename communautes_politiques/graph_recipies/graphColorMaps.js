/*
Array.from(document.querySelectorAll('#GraphLegend li')).map(item => {return {label: item.textContent.trim().split(' ').slice(1).join(' '), color: item.querySelector('span').getAttribute('style').split('color: ').pop()}}).reduce((res, {label, color}) => ({...res, [label]: color}), {})
*/

const acteursColorMap = { 
  "professionnel de la politique": "rgb(212, 194, 255)", 
  "formation politique": "rgb(155, 249, 179)",
   militant: "rgb(145, 137, 224)", 
   candidat: "rgb(225, 111, 138)", 
   campagne: "rgb(1, 228, 200)", 
   association: "rgb(248, 158, 91)", 
   autre: "rgb(65, 164, 124)" 
}
const formeColorMap = { 
  site: "rgb(136, 194, 98)", 
  "réseau social": "rgb(226, 125, 206)", 
  blog: "rgb(198, 132, 83)" 
}

