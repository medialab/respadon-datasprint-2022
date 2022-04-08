/*
Array.from(document.querySelectorAll('#GraphLegend li')).map(item => {return {label: item.textContent.trim().split(' ').slice(1).join(' '), color: item.querySelector('span').getAttribute('style').split('color :').pop()}}).reduce((res, {label, color}) => ({...res, [label]: color}), {})
*/

const acteursColorMap = { 
  "professionnel de la politique": "color: rgb(212, 194, 255);", 
  "formation politique": "color: rgb(155, 249, 179);",
   militant: "color: rgb(145, 137, 224);", 
   candidat: "color: rgb(225, 111, 138);", 
   campagne: "color: rgb(1, 228, 200);", 
   association: "color: rgb(248, 158, 91);", 
   autre: "color: rgb(65, 164, 124);" 
}
const formeColorMap = { 
  site: "color: rgb(136, 194, 98);", 
  "réseau social": "color: rgb(226, 125, 206);", 
  blog: "color: rgb(198, 132, 83);" 
}

