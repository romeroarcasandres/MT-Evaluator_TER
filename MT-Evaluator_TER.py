import os
import pandas as pd
import sacrebleu
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import re

def select_directory():
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title="Select a folder with Excel files")
    return directory

def get_column_mapping(sample_file_path):
    """
    Allow user to specify which columns contain MT and Reference translations
    by showing available columns from a sample file
    """
    try:
        # Read first few rows to show column options
        print("Reading sample file to detect columns...")
        df_sample = pd.read_excel(sample_file_path, nrows=3, dtype=str)
        available_columns = list(df_sample.columns)
        
        print(f"\nAvailable columns in '{os.path.basename(sample_file_path)}':")
        print("=" * 60)
        
        # Display columns with sample data
        for i, col in enumerate(available_columns, 1):
            print(f"{i:2d}. {col}")
            # Show sample data for first few non-empty values
            sample_values = []
            for idx in range(min(3, len(df_sample))):
                if pd.notna(df_sample[col].iloc[idx]) and str(df_sample[col].iloc[idx]).strip():
                    sample_value = str(df_sample[col].iloc[idx]).strip()
                    if len(sample_value) > 50:
                        sample_value = sample_value[:50] + "..."
                    sample_values.append(sample_value)
                    break
            if sample_values:
                print(f"    Sample: {sample_values[0]}")
            print()
        
        # Auto-detect common column names
        mt_suggestions = []
        ref_suggestions = []
        
        common_mt_names = ['machinetranslation', 'mt', 'machine translation', 'translation', 'translated', 
                          'google', 'deepl', 'azure', 'amazon', 'hypothesis', 'hyp', 'output']
        common_ref_names = ['reference', 'human', 'human translation', 'gold', 'target', 'ref', 
                           'ground truth', 'manual', 'expert']
        
        for i, col in enumerate(available_columns, 1):
            col_lower = col.lower().replace('_', ' ').replace('-', ' ')
            if any(name in col_lower for name in common_mt_names):
                mt_suggestions.append(f"{i}")
            if any(name in col_lower for name in common_ref_names):
                ref_suggestions.append(f"{i}")
        
        # Get Machine Translation column
        while True:
            mt_prompt = "\nSelect MACHINE TRANSLATION column number"
            if mt_suggestions:
                mt_prompt += f" (suggested: {', '.join(mt_suggestions)})"
            mt_prompt += ": "
            
            try:
                mt_choice = input(mt_prompt).strip()
                if not mt_choice:
                    if mt_suggestions:
                        mt_choice = mt_suggestions[0]
                    else:
                        print("Please enter a column number.")
                        continue
                
                mt_index = int(mt_choice) - 1
                if 0 <= mt_index < len(available_columns):
                    mt_column = available_columns[mt_index]
                    print(f"Selected MT column: '{mt_column}'")
                    break
                else:
                    print(f"Please enter a number between 1 and {len(available_columns)}")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get Reference Translation column
        while True:
            ref_prompt = "\nSelect REFERENCE (Human) TRANSLATION column number"
            if ref_suggestions:
                ref_prompt += f" (suggested: {', '.join(ref_suggestions)})"
            ref_prompt += ": "
            
            try:
                ref_choice = input(ref_prompt).strip()
                if not ref_choice:
                    if ref_suggestions:
                        ref_choice = ref_suggestions[0]
                    else:
                        print("Please enter a column number.")
                        continue
                
                ref_index = int(ref_choice) - 1
                if 0 <= ref_index < len(available_columns):
                    if ref_index == mt_index:
                        print("Machine Translation and Reference columns must be different. Please choose a different column.")
                        continue
                    ref_column = available_columns[ref_index]
                    print(f"Selected Reference column: '{ref_column}'")
                    break
                else:
                    print(f"Please enter a number between 1 and {len(available_columns)}")
            except ValueError:
                print("Please enter a valid number.")
        
        # Confirm selection
        print(f"\n" + "="*60)
        print("COLUMN SELECTION SUMMARY:")
        print(f"Machine Translation: '{mt_column}'")
        print(f"Reference Translation: '{ref_column}'")
        print("="*60)
        
        confirm = input("\nIs this correct? (y/n, default=y): ").strip().lower()
        if confirm in ['n', 'no']:
            print("Column selection cancelled.")
            return {'mt_column': None, 'ref_column': None, 'cancelled': True}
        
        return {'mt_column': mt_column, 'ref_column': ref_column, 'cancelled': False}
        
    except Exception as e:
        print(f"Error reading sample file: {str(e)}")
        print("Please check if the file exists and is a valid Excel file.")
        return {'mt_column': None, 'ref_column': None, 'cancelled': True}

def extract_language_code(filename):
    name, _ = os.path.splitext(filename)
    parts = name.split("_")
    return parts[-1] if len(parts) > 1 else "unknown"

def detect_language_family(language_code):
    """Detect language family based on language code for appropriate tokenization"""
    
    # Chinese variants
    chinese_codes = ['zh', 'zh-cn', 'zh-tw', 'zh-sg', 'zh-hk', 'cmn', 'chi']
    
    # Japanese
    japanese_codes = ['ja', 'jp', 'jpn']
    
    # Korean  
    korean_codes = ['ko', 'kr', 'kor']
    
    # Thai
    thai_codes = ['th', 'tha', 'thai']
    
    # Vietnamese
    vietnamese_codes = ['vi', 'vn', 'vie']
    
    # Other Asian languages that benefit from character-based tokenization
    other_asian_codes = ['my', 'mya', 'burmese', 'km', 'khm', 'khmer', 'lo', 'lao']
    
    # Arabic and related scripts
    arabic_codes = ['ar', 'ara', 'arabic', 'he', 'heb', 'hebrew', 'fa', 'per', 'persian', 'ur', 'urd', 'urdu']
    
    # Cyrillic languages
    cyrillic_codes = ['ru', 'uk', 'bg', 'sr', 'mk', 'be', 'kk', 'uz', 'ky', 'tg', 'mn']
    
    lang_lower = language_code.lower()
    
    if any(code in lang_lower for code in chinese_codes):
        return 'chinese'
    elif any(code in lang_lower for code in japanese_codes):
        return 'japanese'
    elif any(code in lang_lower for code in korean_codes):
        return 'korean'
    elif any(code in lang_lower for code in thai_codes):
        return 'thai'
    elif any(code in lang_lower for code in vietnamese_codes):
        return 'vietnamese'
    elif any(code in lang_lower for code in other_asian_codes):
        return 'asian_char_based'
    elif any(code in lang_lower for code in arabic_codes):
        return 'arabic'
    elif any(code in lang_lower for code in cyrillic_codes):
        return 'cyrillic'
    else:
        return 'default'

def preprocess_chinese_text(text):
    """Basic Chinese text preprocessing"""
    if not isinstance(text, str):
        return ""
    # Remove extra whitespace but preserve Chinese punctuation
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def preprocess_japanese_text(text):
    """Basic Japanese text preprocessing"""
    if not isinstance(text, str):
        return ""
    # Remove extra whitespace but preserve Japanese punctuation
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def preprocess_korean_text(text):
    """Korean text preprocessing with basic Hangul handling"""
    if not isinstance(text, str):
        return ""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def preprocess_thai_text(text):
    """Thai text preprocessing"""
    if not isinstance(text, str):
        return ""
    # Thai doesn't use spaces between words, so be careful with whitespace
    text = re.sub(r'\n+', ' ', text.strip())
    return text

def preprocess_asian_char_based(text):
    """General preprocessing for character-based Asian languages"""
    if not isinstance(text, str):
        return ""
    # Preserve character sequences, minimal whitespace normalization
    text = re.sub(r'\n+', ' ', text.strip())
    text = re.sub(r'\s{2,}', ' ', text)
    return text

def preprocess_arabic_text(text):
    """Arabic/Hebrew/Persian text preprocessing"""
    if not isinstance(text, str):
        return ""
    # Basic RTL text preprocessing
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def clean_text(text, language_family):
    """Enhanced text cleaning based on language family"""
    if not isinstance(text, str):
        return ""
    
    if language_family == 'chinese':
        return preprocess_chinese_text(text)
    elif language_family == 'japanese':
        return preprocess_japanese_text(text)
    elif language_family == 'korean':
        return preprocess_korean_text(text)
    elif language_family == 'thai':
        return preprocess_thai_text(text)
    elif language_family == 'vietnamese':
        return preprocess_asian_char_based(text)
    elif language_family == 'asian_char_based':
        return preprocess_asian_char_based(text)
    elif language_family == 'arabic':
        return preprocess_arabic_text(text)
    else:
        # Default cleaning for Latin scripts and Cyrillic
        return " ".join(text.strip().split())

def check_sacrebleu_ter_support():
    """Check which TER parameters are supported in the current SacreBLEU version"""
    import inspect
    
    supported_params = {}
    
    try:
        # Get TER constructor signature
        ter_signature = inspect.signature(sacrebleu.TER.__init__)
        params = list(ter_signature.parameters.keys())
        
        # Check for common TER parameters
        supported_params['case_sensitive'] = 'case_sensitive' in params
        supported_params['normalize'] = 'normalize' in params
        supported_params['no_punct'] = 'no_punct' in params
        supported_params['asian_support'] = 'asian_support' in params
        supported_params['no_whitespace'] = 'no_whitespace' in params
        
        return supported_params
    except Exception as e:
        # Silent fallback - no print statement here
        return {}

def get_ter_options(language_family, supported_params):
    """Get TER computation options based on language family and supported parameters"""
    
    ter_options = {}
    
    # Only add parameters that are supported
    if supported_params.get('case_sensitive', False):
        ter_options['case_sensitive'] = False
    
    if supported_params.get('normalize', False):
        ter_options['normalize'] = True
    
    if supported_params.get('no_punct', False):
        ter_options['no_punct'] = False
    
    if supported_params.get('asian_support', False):
        if language_family in ['chinese', 'japanese', 'korean', 'thai', 'vietnamese', 'asian_char_based']:
            ter_options['asian_support'] = True
        else:
            ter_options['asian_support'] = False
    
    if supported_params.get('no_whitespace', False):
        ter_options['no_whitespace'] = False
    
    return ter_options

def compute_ter_score(hypotheses, references, language_family, supported_params):
    """Compute TER score with appropriate options for the language"""
    try:
        # Get TER options based on language family and supported parameters
        ter_options = get_ter_options(language_family, supported_params)
        
        if ter_options:
            # Create TER metric with supported options
            ter_metric = sacrebleu.TER(**ter_options)
            # Removed the print statement for cleaner output
        else:
            # Use basic TER if no options are supported
            ter_metric = sacrebleu.TER()
            # Removed the print statement for cleaner output
        
        # Compute TER score
        ter_score = ter_metric.corpus_score(hypotheses, references)
        
        return ter_score.score
        
    except Exception as e:
        print(f"  Warning: Error with TER computation ({e}), trying basic TER")
        try:
            # Fallback to basic TER without any options
            basic_ter = sacrebleu.TER()
            ter_score = basic_ter.corpus_score(hypotheses, references)
            return ter_score.score
        except Exception as e2:
            print(f"  Error: Basic TER computation also failed ({e2})")
            return None

def process_excel_files(directory, mt_column_name, ref_column_name):
    ter_results = []
    
    # Check SacreBLEU TER support once at the beginning (silently)
    supported_params = check_sacrebleu_ter_support()
    
    for file in os.listdir(directory):
        if file.endswith(".xlsx"):
            file_path = os.path.join(directory, file)
            language_code = extract_language_code(file)
            language_family = detect_language_family(language_code)
            
            print(f"Processing {file} (Language: {language_code}, Family: {language_family})")
            
            try:
                df = pd.read_excel(file_path, dtype=str)  # Ensure text columns are treated as strings
                
                # Check if the specified columns exist
                if mt_column_name not in df.columns or ref_column_name not in df.columns:
                    missing_cols = []
                    if mt_column_name not in df.columns:
                        missing_cols.append(f"'{mt_column_name}'")
                    if ref_column_name not in df.columns:
                        missing_cols.append(f"'{ref_column_name}'")
                    
                    print(f"  Skipping {file}: Missing columns {', '.join(missing_cols)}")
                    print(f"  Available columns: {', '.join(df.columns.tolist())}")
                    ter_results.append(f"{file}\t{language_code}\t{language_family}\tERROR: Missing columns {', '.join(missing_cols)}")
                    continue
                
                # Clean and extract text with language-specific preprocessing
                df[mt_column_name] = df[mt_column_name].fillna("").apply(
                    lambda x: clean_text(x, language_family)
                )
                df[ref_column_name] = df[ref_column_name].fillna("").apply(
                    lambda x: clean_text(x, language_family)
                )
                
                # Filter out empty translations
                valid_rows = (df[mt_column_name].str.strip() != '') & (df[ref_column_name].str.strip() != '')
                df_filtered = df[valid_rows]
                
                if len(df_filtered) == 0:
                    print(f"  Warning: No valid text pairs found in {file}")
                    ter_results.append(f"{file}\t{language_code}\t{language_family}\tERROR: No valid text data")
                    continue
                
                # Prepare data for TER calculation
                hypotheses = df_filtered[mt_column_name].tolist()
                references = [df_filtered[ref_column_name].tolist()]  # TER expects list of reference lists
                
                print(f"  Computing TER for {len(hypotheses)} sentence pairs...")
                
                # Compute TER score
                ter_score = compute_ter_score(hypotheses, references, language_family, supported_params)
                
                if ter_score is not None:
                    ter_results.append(f"{file}\t{language_code}\t{language_family}\t{ter_score:.2f}")
                    print(f"  TER Score = {ter_score:.2f}")
                else:
                    print(f"  Failed to compute TER score")
                    ter_results.append(f"{file}\t{language_code}\t{language_family}\tERROR: TER computation failed")
                
                # Save individual text files for debugging if needed
                mt_output_file = os.path.join(directory, f"MachineTranslation_{language_code}.txt")
                ref_output_file = os.path.join(directory, f"Reference_{language_code}.txt")
                
                with open(mt_output_file, "w", encoding="utf-8") as f:
                    for line in hypotheses:
                        f.write(line + "\n")
                
                with open(ref_output_file, "w", encoding="utf-8") as f:
                    for line in references[0]:
                        f.write(line + "\n")
                
            except Exception as e:
                print(f"  Error processing {file}: {e}")
                ter_results.append(f"{file}\t{language_code}\tUNKNOWN\tERROR: {str(e)}")
    
    # Save TER scores to a tab-separated file with enhanced headers
    ter_score_file = os.path.join(directory, "ter_scores.txt")
    with open(ter_score_file, "w", encoding="utf-8") as f:
        f.write("Filename\tLanguage_Code\tLanguage_Family\tTER_Score\n")
        f.write(f"# Machine Translation Column: {mt_column_name}\n")
        f.write(f"# Reference Translation Column: {ref_column_name}\n")
        f.write(f"# Total Files Processed: {len(ter_results)}\n")
        f.write("# " + "="*50 + "\n")
        f.write("\n".join(ter_results))
    
    print(f"\nTER scores saved to {ter_score_file}")
    print(f"Processed {len(ter_results)} files total")
    print(f"Machine Translation Column: '{mt_column_name}'")
    print(f"Reference Translation Column: '{ref_column_name}'")

if __name__ == "__main__":
    print("Enhanced Multi-Language TER Evaluation Script")
    print("=" * 50)
    print("Supports: Chinese, Japanese, Korean, Thai, Vietnamese,")
    print("          Arabic, Hebrew, Persian, Burmese, Khmer, Lao,")
    print("          Cyrillic scripts, and more")
    print("=" * 50)
    
    # Step 1: Select directory
    selected_directory = select_directory()
    if not selected_directory:
        print("No directory selected. Exiting.")
        exit()
    
    # Step 2: Find Excel files and get column mapping
    excel_files = [f for f in os.listdir(selected_directory) if f.endswith('.xlsx')]
    
    if not excel_files:
        print("No Excel files found in the selected directory.")
        messagebox.showerror("Error", "No Excel files found in the selected directory.")
        exit()
    
    print(f"Found {len(excel_files)} Excel file(s)")
    
    # Use first Excel file as sample for column selection
    sample_file = os.path.join(selected_directory, excel_files[0])
    print(f"Using '{excel_files[0]}' as sample for column selection...")
    
    # Step 3: Get column mapping from user
    print("Opening column selection dialog...")
    column_mapping = get_column_mapping(sample_file)
    
    if column_mapping['cancelled']:
        print("Column selection cancelled. Exiting.")
        exit()
    
    mt_column = column_mapping['mt_column']
    ref_column = column_mapping['ref_column']
    
    print(f"\nColumn selection completed successfully!")
    print(f"Selected columns:")
    print(f"  Machine Translation: '{mt_column}'")
    print(f"  Reference Translation: '{ref_column}'")
    print("\nStarting TER evaluation...")
    print("-" * 50)
    
    # Step 4: Process all files with selected columns
    process_excel_files(selected_directory, mt_column, ref_column)