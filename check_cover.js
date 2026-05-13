const fs = require('fs');
const d = JSON.parse(fs.readFileSync('public/scenes.json', 'utf8'));
Object.values(d).forEach(s => {
  console.log(s.title, '-> coverUrl:', JSON.stringify(s.coverUrl));
});
