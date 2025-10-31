from app import app
from models import db, Gene, Mutant, SizeMetric, BehaviorData
import pandas as pd
import os
import sys

def create_excel_template():
    """
    Create an Excel template file with the correct structure
    """
    template_file = r"C:\Users\pkrap\OneDrive\Desktop\analysis_results_20250922_165600.xlsx"
    
    with pd.ExcelWriter(template_file, engine='openpyxl') as writer:
        # Genes sheet
        genes_template = pd.DataFrame({
            'name': ['sox10', 'mitfa', 'fgf8'],
            'description': [
                'SRY-box transcription factor 10',
                'Melanogenesis associated transcription factor',
                'Fibroblast growth factor 8'
            ]
        })
        genes_template.to_excel(writer, sheet_name='genes', index=False)
        
        # Mutants sheet
        mutants_template = pd.DataFrame({
            'gene_name': ['sox10', 'mitfa', 'fgf8'],
            'mutant_name': ['sox10-/-', 'mitfa-/-', 'fgf8-/-'],
            'phenotype': [
                'Pigmentation defects, no melanocytes',
                'Nacre, lack of melanophores',
                'Brain and jaw defects'
            ],
            'image_path': [
                '/static/images/sox10.jpg',
                '/static/images/mitfa.jpg',
                '/static/images/fgf8.jpg'
            ]
        })
        mutants_template.to_excel(writer, sheet_name='mutants', index=False)
        
        # Size metrics sheet
        size_metrics_template = pd.DataFrame({
            'mutant_name': ['sox10-/-', 'sox10-/-', 'sox10-/-', 'mitfa-/-', 'mitfa-/-'],
            'age_dpf': [1, 2, 3, 1, 2],
            'body_length': [3.2, 3.8, 4.5, 3.5, 4.1],
            'head_width': [0.35, 0.40, 0.45, 0.38, 0.43],
            'tail_length': [2.0, 2.5, 3.0, 2.2, 2.7],
            'weight_mg': [2.5, 4.2, 6.8, 2.8, 4.5],
            'sample_size': [15, 20, 18, 12, 16]
        })
        size_metrics_template.to_excel(writer, sheet_name='size_metrics', index=False)
        
        # Behavior data sheet
        behavior_template = pd.DataFrame({
            'mutant_name': ['sox10-/-', 'sox10-/-', 'sox10-/-', 'mitfa-/-', 'mitfa-/-'],
            'behavior_type': ['swimming_speed', 'swimming_speed', 'swimming_speed', 
                            'startle_response', 'startle_response'],
            'time_point': [0, 2, 4, 0, 2],
            'value': [10.5, 12.3, 11.8, 75.2, 68.5],
            'unit': ['mm/s', 'mm/s', 'mm/s', '%', '%']
        })
        behavior_template.to_excel(writer, sheet_name='behavior_data', index=False)
    
    print(f"✅ Template created: {template_file}")
    print("\nSheet structure:")
    print("  1. genes: name, description")
    print("  2. mutants: gene_name, mutant_name, phenotype, image_path")
    print("  3. size_metrics: mutant_name, age_dpf, body_length, head_width, tail_length, weight_mg, sample_size")
    print("  4. behavior_data: mutant_name, behavior_type, time_point, value, unit")


def validate_excel_file(file_path):
    """
    Validate that the Excel file has the required sheets and columns
    """
    required_sheets = ['genes', 'mutants', 'size_metrics', 'behavior_data']
    
    try:
        excel_file = pd.ExcelFile(file_path)
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return False
    
    # Check if all required sheets exist
    missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_file.sheet_names]
    if missing_sheets:
        print(f"❌ Missing sheets: {', '.join(missing_sheets)}")
        return False
    
    # Validate genes sheet
    genes_df = pd.read_excel(file_path, sheet_name='genes')
    required_genes_cols = ['name', 'description']
    if not all(col in genes_df.columns for col in required_genes_cols):
        print(f"❌ 'genes' sheet missing columns. Required: {required_genes_cols}")
        return False
    
    # Validate mutants sheet
    mutants_df = pd.read_excel(file_path, sheet_name='mutants')
    required_mutants_cols = ['gene_name', 'mutant_name', 'phenotype']
    if not all(col in mutants_df.columns for col in required_mutants_cols):
        print(f"❌ 'mutants' sheet missing columns. Required: {required_mutants_cols}")
        return False
    
    # Validate size_metrics sheet
    size_metrics_df = pd.read_excel(file_path, sheet_name='size_metrics')
    required_size_cols = ['mutant_name', 'age_dpf', 'body_length']
    if not all(col in size_metrics_df.columns for col in required_size_cols):
        print(f"❌ 'size_metrics' sheet missing columns. Required: {required_size_cols}")
        return False
    
    # Validate behavior_data sheet
    behavior_df = pd.read_excel(file_path, sheet_name='behavior_data')
    required_behavior_cols = ['mutant_name', 'behavior_type', 'time_point', 'value', 'unit']
    if not all(col in behavior_df.columns for col in required_behavior_cols):
        print(f"❌ 'behavior_data' sheet missing columns. Required: {required_behavior_cols}")
        return False
    
    print("✅ Excel file validation passed!")
    return True


def populate_from_excel(file_path, clear_existing=True):
    """
    Populate database from Excel file
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    if not validate_excel_file(file_path):
        return False
    
    with app.app_context():
        # Clear existing data if requested
        if clear_existing:
            print("🗑️  Clearing existing data...")
            db.drop_all()
            db.create_all()
        
        try:
            # Read Excel sheets
            genes_df = pd.read_excel(file_path, sheet_name='genes')
            mutants_df = pd.read_excel(file_path, sheet_name='mutants')
            size_metrics_df = pd.read_excel(file_path, sheet_name='size_metrics')
            behavior_df = pd.read_excel(file_path, sheet_name='behavior_data')
            
            # Replace NaN with None
            genes_df = genes_df.where(pd.notnull(genes_df), None)
            mutants_df = mutants_df.where(pd.notnull(mutants_df), None)
            size_metrics_df = size_metrics_df.where(pd.notnull(size_metrics_df), None)
            behavior_df = behavior_df.where(pd.notnull(behavior_df), None)
            
            # Import genes
            print("\n📥 Importing genes...")
            gene_map = {}  # Map gene names to gene objects
            
            for _, row in genes_df.iterrows():
                gene = Gene(
                    name=row['name'],
                    description=row['description']
                )
                db.session.add(gene)
                db.session.flush()  # Get the gene_id
                gene_map[row['name']] = gene
                print(f"   ✓ Added gene: {row['name']}")
            
            db.session.commit()
            
            # Import mutants
            print("\n📥 Importing mutants...")
            mutant_map = {}  # Map mutant names to mutant objects
            
            for _, row in mutants_df.iterrows():
                gene_name = row['gene_name']
                if gene_name not in gene_map:
                    print(f"   ⚠️  Warning: Gene '{gene_name}' not found for mutant '{row['mutant_name']}'")
                    continue
                
                mutant = Mutant(
                    gene_id=gene_map[gene_name].gene_id,
                    mutant_name=row['mutant_name'],
                    phenotype=row['phenotype'],
                    image_path=row.get('image_path')
                )
                db.session.add(mutant)
                db.session.flush()
                mutant_map[row['mutant_name']] = mutant
                print(f"   ✓ Added mutant: {row['mutant_name']}")
            
            db.session.commit()
            
            # Import size metrics
            print("\n📥 Importing size metrics...")
            size_count = 0
            
            for _, row in size_metrics_df.iterrows():
                mutant_name = row['mutant_name']
                if mutant_name not in mutant_map:
                    print(f"   ⚠️  Warning: Mutant '{mutant_name}' not found for size metric")
                    continue
                
                metric = SizeMetric(
                    mutant_id=mutant_map[mutant_name].mutant_id,
                    age_dpf=row.get('age_dpf'),
                    body_length=row.get('body_length'),
                    head_width=row.get('head_width'),
                    tail_length=row.get('tail_length'),
                    weight_mg=row.get('weight_mg'),
                    sample_size=row.get('sample_size')
                )
                db.session.add(metric)
                size_count += 1
            
            db.session.commit()
            print(f"   ✓ Added {size_count} size metric records")
            
            # Import behavior data
            print("\n📥 Importing behavior data...")
            behavior_count = 0
            
            for _, row in behavior_df.iterrows():
                mutant_name = row['mutant_name']
                if mutant_name not in mutant_map:
                    print(f"   ⚠️  Warning: Mutant '{mutant_name}' not found for behavior data")
                    continue
                
                behavior = BehaviorData(
                    mutant_id=mutant_map[mutant_name].mutant_id,
                    behavior_type=row['behavior_type'],
                    time_point=row['time_point'],
                    value=row['value'],
                    unit=row['unit']
                )
                db.session.add(behavior)
                behavior_count += 1
            
            db.session.commit()
            print(f"   ✓ Added {behavior_count} behavior data records")
            
            # Summary
            print("\n" + "="*50)
            print("✅ Database populated successfully!")
            print("="*50)
            print(f"   📊 Genes: {len(gene_map)}")
            print(f"   🐟 Mutants: {len(mutant_map)}")
            print(f"   📏 Size metrics: {size_count}")
            print(f"   📈 Behavior records: {behavior_count}")
            print("="*50)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error importing data: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """
    Main function with command-line interface
    """
    print("="*50)
    print("🐟 Zebrafish Database Populator")
    print("="*50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'template':
            create_excel_template()
        elif command == 'import':
            if len(sys.argv) < 3:
                print("❌ Usage: python populate_db.py import <excel_file>")
                sys.exit(1)
            excel_file = sys.argv[2]
            populate_from_excel(excel_file)
        elif command == 'validate':
            if len(sys.argv) < 3:
                print("❌ Usage: python populate_db.py validate <excel_file>")
                sys.exit(1)
            excel_file = sys.argv[2]
            validate_excel_file(excel_file)
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
    else:
        print_usage()


def print_usage():
    """
    Print usage instructions
    """
    print("\nUsage:")
    print("  python populate_db.py template           - Create Excel template")
    print("  python populate_db.py import <file>      - Import data from Excel")
    print("  python populate_db.py validate <file>    - Validate Excel file")
    print("\nExample:")
    print("  python populate_db.py template")
    print("  python populate_db.py import zebrafish_data_template.xlsx")


if __name__ == '__main__':
    main()