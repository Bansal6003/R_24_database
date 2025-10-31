from flask import Flask, render_template, jsonify, request
from models import db, Gene, Mutant, SizeMetric, BehaviorData
import os
import json

app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'zebrafish.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/mutants', methods=['GET'])
def get_mutants():
    """Get all mutants for dropdown"""
    mutants = Mutant.query.all()
    return jsonify([m.to_dict() for m in mutants])


@app.route('/api/mutant/<int:mutant_id>', methods=['GET'])
def get_mutant(mutant_id):
    """Get specific mutant details"""
    mutant = Mutant.query.get_or_404(mutant_id)
    return jsonify(mutant.to_dict())


@app.route('/api/size-metrics/<int:mutant_id>', methods=['GET'])
def get_size_metrics(mutant_id):
    """Get size metrics for a specific mutant"""
    metrics = SizeMetric.query.filter_by(mutant_id=mutant_id).all()
    return jsonify([m.to_dict() for m in metrics])


@app.route('/api/behavior-data/<int:mutant_id>', methods=['GET'])
def get_behavior_data(mutant_id):
    """Get behavior data for plotting"""
    behavior_data = BehaviorData.query.filter_by(mutant_id=mutant_id).all()
    
    # Group by behavior type
    grouped_data = {}
    for data in behavior_data:
        behavior_type = data.behavior_type
        if behavior_type not in grouped_data:
            grouped_data[behavior_type] = {
                'time_points': [],
                'values': [],
                'unit': data.unit
            }
        grouped_data[behavior_type]['time_points'].append(data.time_point)
        grouped_data[behavior_type]['values'].append(data.value)
    
    return jsonify(grouped_data)


@app.route('/api/search', methods=['GET'])
def search_mutants():
    """Search mutants by phenotype or gene"""
    phenotype = request.args.get('phenotype', '')
    gene_name = request.args.get('gene', '')
    
    query = Mutant.query
    
    if phenotype:
        query = query.filter(Mutant.phenotype.contains(phenotype))
    
    if gene_name:
        query = query.join(Gene).filter(Gene.name.contains(gene_name))
    
    mutants = query.all()
    return jsonify([m.to_dict() for m in mutants])


@app.route('/api/genes', methods=['GET'])
def get_genes():
    """Get all genes"""
    genes = Gene.query.all()
    return jsonify([g.to_dict() for g in genes])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)