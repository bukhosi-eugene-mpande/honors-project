#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Function to recursively replace NaN values with null
function replaceNaN(obj) {
  if (obj === null || obj === undefined) {
    return obj;
  }
  
  if (typeof obj === 'number' && isNaN(obj)) {
    return null;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(replaceNaN);
  }
  
  if (typeof obj === 'object') {
    const result = {};
    for (const [key, value] of Object.entries(obj)) {
      result[key] = replaceNaN(value);
    }
    return result;
  }
  
  return obj;
}

// Files to process
const files = [
  'public/graded_stats.json',
  'public/graded_stats/graded_stats_llm_one_shot.json',
  'public/graded_stats/stats_results_llm_with_nlp.json',
  'public/graded_stats/stats_results_model_answer.json'
];

console.log('🔧 Fixing NaN values in JSON files...\n');

files.forEach(filePath => {
  try {
    if (fs.existsSync(filePath)) {
      console.log(`Processing: ${filePath}`);
      
      // Read the file
      const content = fs.readFileSync(filePath, 'utf8');
      
      // Parse JSON
      const data = JSON.parse(content);
      
      // Replace NaN values
      const fixedData = replaceNaN(data);
      
      // Write back to file
      fs.writeFileSync(filePath, JSON.stringify(fixedData, null, 2));
      
      console.log(`✅ Fixed: ${filePath}`);
    } else {
      console.log(`⚠️  File not found: ${filePath}`);
    }
  } catch (error) {
    console.error(`❌ Error processing ${filePath}:`, error.message);
  }
});

console.log('\n🎉 All files processed!');
