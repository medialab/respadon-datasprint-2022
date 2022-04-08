const fs = require('fs');
const y2012 = fs.readFileSync('../data/melenchon_2012.csv', 'utf8');
const y2017 = fs.readFileSync('../data/melenchon_2017.csv', 'utf8');
const y2022 = fs.readFileSync('../data/melenchon_2022.csv', 'utf8');

import('d3-dsv')
  .then(dsv => {
    const outputs = [
      {
        field: 'forme éditoriale (TAGS)',
        output: '../data/evolution_formes.csv',
      },
      {
        field: 'acteur (TAGS)',
        output: '../data/evolution_acteurs.csv',
      },

    ]
    const years = [
      {
        year: 2012,
        str: y2012,
        csv: dsv.csvParse(y2012),
        labels: new Set()
      },
      {
        year: 2017,
        str: y2017,
        csv: dsv.csvParse(y2017),
        labels: new Set()
      },
      {
        year: 2022,
        str: y2022,
        csv: dsv.csvParse(y2022),
        labels: new Set()
      }
    ]
    years.forEach(({csv, labels}) => {
      csv.forEach(obj => {
        labels.add(obj['NAME'])
      })
    })
    // let flowData = [];
    // for (yearIndex in years) {
    //   const year = years[yearIndex];
    //   const next = years[+yearIndex + 1];
    //   if (!next) {
    //     const prev = years[+yearIndex - 1];
    //     const onlyInCurrent = [...year.labels]
    //     .filter(label => !prev.labels.has(label));
    //     console.log(onlyInCurrent.length, 'only in ', year.year)
    //   } else {
    //     const bridging = [...year.labels]
    //     .filter(label => next.labels.has(label));
    //     flowData = [
    //       ...flowData
    //     ]
    //   }
    // }
    outputs.forEach(({ field, output }) => {
      let metricsOutput = [];
      const valuesMap = {}
      years.forEach(({ year, str, csv }, yearIndex) => {
        // console.log('csv', csv);
        csv.forEach(obj => {
          let key = obj[field];
          key = key === '' ? 'pas de clé' : key;
          const indegree = +obj['INDEGREE']
          const totalKnownPages = +obj['TOTAL KNOWN PAGES'];
          if (!valuesMap[key]) {
            valuesMap[key] = {}
          }
          if (!valuesMap[key][year]) {
            valuesMap[key][year] = {
              indegree: 0,
              totalKnownPages: 0,
              count: 0
            }
          }
          valuesMap[key][year] = {
            indegree: valuesMap[key][year].indegree + indegree,
            totalKnownPages: valuesMap[key][year].totalKnownPages + totalKnownPages,
            count: valuesMap[key][year].count + 1
          }
        });
      });
      Object.entries(valuesMap).forEach(([key, years]) => {
        Object.entries(years).forEach(([year, metrics]) => {
          metricsOutput.push({
            year,
            key,
            ...metrics,
          })
        })
      })
      fs.writeFileSync(output, dsv.csvFormat(metricsOutput), 'utf8')
    })

  })
