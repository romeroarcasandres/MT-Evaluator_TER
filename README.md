# MT-Evaluator_TER
Advanced Translation Error Rate (TER) evaluation tool with multi-language support and interactive column selection

## Overview:
This comprehensive script evaluates machine translation quality using Translation Error Rate (TER) metrics across multiple languages and writing systems. It provides an interactive interface for selecting Excel files containing translation data, automatically detects language families for appropriate text preprocessing, and generates detailed TER score reports. The script intelligently handles various writing systems including Chinese, Japanese, Korean, Thai, Arabic, Cyrillic, and Latin scripts while providing users full control over column selection for machine translation and reference translation data.

## Requirements:
- Python 3.6+
- tkinter library (for file dialog interface)
- pandas library (for Excel file processing)
- sacrebleu library (for TER computation)
- openpyxl library (for Excel file reading)
- re library (for text preprocessing)
- os library (for file operations)

## Files
MT-Evaluator_TER.py

## Installation
Before running the script, install the required dependencies:
```bash
pip install pandas sacrebleu openpyxl
```

## Usage
1. Run the script: `python MT-Evaluator_TER.py`
2. A file dialog will prompt you to select a directory containing Excel files
3. The script analyzes the first Excel file and displays all available columns with sample data
4. Select the machine translation column by entering the corresponding number
5. Select the reference (human) translation column by entering the corresponding number
6. The script processes all Excel files in the directory and generates:
   - Individual text files for machine translation and reference data
   - A comprehensive TER scores report (`ter_scores.txt`)

## Key Features
- **Multi-Language Support**: Handles 15+ language families with specialized preprocessing
- **Automatic Language Detection**: Extracts language codes from filenames and applies appropriate processing
- **Smart Column Detection**: Auto-suggests likely machine translation and reference columns
- **Interactive Column Selection**: Visual column browser with sample data preview
- **Advanced Text Preprocessing**: Language-specific cleaning for optimal TER computation
- **Robust Error Handling**: Gracefully handles missing columns, empty data, and file access errors
- **Comprehensive Reporting**: Detailed TER scores with metadata and processing statistics
- **SacreBLEU Integration**: Automatic detection of available TER parameters and fallback options
- **Unicode Support**: Full UTF-8 encoding support for international character sets
- **Batch Processing**: Processes multiple Excel files in a single run

## Supported Languages and Writing Systems
- **Chinese Variants**: Simplified/Traditional Chinese (zh, zh-cn, zh-tw, cmn)
- **Japanese**: Hiragana, Katakana, Kanji (ja, jp, jpn)
- **Korean**: Hangul and Hanja (ko, kr, kor)
- **Southeast Asian**: Thai (th), Vietnamese (vi), Burmese (my), Khmer (km), Lao (lo)
- **Arabic Script**: Arabic (ar), Hebrew (he), Persian (fa), Urdu (ur)
- **Cyrillic Scripts**: Russian (ru), Ukrainian (uk), Bulgarian (bg), Serbian (sr), etc.
- **Latin Scripts**: English, Spanish, French, German, and other European languages

## Language-Specific Preprocessing
- **Chinese/Japanese/Korean**: Character-based tokenization with punctuation preservation
- **Thai**: Word boundary handling for non-spaced text
- **Arabic/Hebrew**: Right-to-left text normalization
- **Cyrillic**: Whitespace normalization with script-specific handling
- **Latin Scripts**: Standard tokenization and normalization

## File Naming Convention
Excel files should follow the pattern: `[description]_[language_code].xlsx`

Examples:
- `translations_en.xlsx` (English)
- `mt_output_zh-cn.xlsx` (Simplified Chinese)
- `results_ja.xlsx` (Japanese)

## Example Usage
For a directory containing:
```
translations_en.xlsx
translations_es.xlsx
translations_zh.xlsx
```

The script will:
1. Display available columns from the first file
2. Allow selection of MT and Reference columns
3. Process each file with language-appropriate preprocessing
4. Generate TER scores for each language pair
5. Create a summary report with all results

## Column Selection Interface
```
Available columns in 'translations_en.xlsx':
============================================================
 1. source_text
    Sample: The quick brown fox jumps over the lazy dog
 
 2. machine_translation
    Sample: Le renard brun rapide saute par-dessus le chien paresseux
 
 3. human_reference
    Sample: Le renard brun et rapide saute par-dessus le chien paresseux
 
 4. translation_model
    Sample: google_translate_v2
```

## Output Files
- **Individual Text Files**: `MachineTranslation_[lang].txt`, `Reference_[lang].txt`
- **TER Scores Report**: `ter_scores.txt` with columns:
  - Filename
  - Language Code
  - Language Family
  - TER Score

## TER Score Interpretation
- **Lower scores indicate better translation quality**
- TER measures the minimum number of edits needed to change hypothesis to match reference
- Typical ranges (it depends):
  - 0.0-0.2: Excellent quality
  - 0.2-0.4: Good quality
  - 0.4-0.6: Fair quality
  - 0.6+: Poor quality

## Important Notes
- Ensure Excel files contain valid translation data in separate columns
- Language codes in filenames help optimize preprocessing algorithms
- The script handles inconsistent data gracefully with detailed error reporting
- Empty or missing translations are automatically filtered out
- Complex formatting in Excel cells is preserved during text extraction
- All processing uses UTF-8 encoding for international character support
- SacreBLEU version compatibility is automatically detected and handled

## Error Handling
- Invalid Excel files are detected and reported with clear error messages
- Missing or misnamed columns are handled with detailed feedback
- File access errors are handled gracefully with user-friendly notifications
- Missing dependencies are detected at startup with installation instructions
- Language detection failures default to standard preprocessing
- TER computation errors trigger automatic fallback to basic metrics

## Advanced Features
- **Dynamic TER Configuration**: Automatically adapts TER parameters based on SacreBLEU version
- **Language Family Detection**: Sophisticated algorithm for identifying script families
- **Preprocessing Pipeline**: Multi-stage text cleaning optimized for each language
- **Batch Validation**: Pre-processes all files to identify potential issues
- **Progress Reporting**: Real-time feedback on processing status
- **Debug Output**: Optional detailed text files for troubleshooting

## Troubleshooting
- **"No valid text pairs found"**: Check for empty columns or incorrect column selection
- **"TER computation failed"**: Verify SacreBLEU installation and text encoding
- **"Missing columns"**: Ensure column names match across all Excel files
- **Language detection issues**: Verify filename format includes language code

## License
This project is governed by the CC BY-NC 4.0 license. For comprehensive details, kindly refer to the LICENSE file included with this project.
