from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Gene(db.Model):
    __tablename__ = 'genes'
    
    gene_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Relationship
    mutants = db.relationship('Mutant', backref='gene', lazy=True)
    
    def to_dict(self):
        return {
            'gene_id': self.gene_id,
            'name': self.name,
            'description': self.description
        }


class Mutant(db.Model):
    __tablename__ = 'mutants'
    
    mutant_id = db.Column(db.Integer, primary_key=True)
    gene_id = db.Column(db.Integer, db.ForeignKey('genes.gene_id'), nullable=False)
    mutant_name = db.Column(db.String(100), unique=True, nullable=False)
    phenotype = db.Column(db.String(200))
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    size_metrics = db.relationship('SizeMetric', backref='mutant', lazy=True)
    behavior_data = db.relationship('BehaviorData', backref='mutant', lazy=True)
    
    def to_dict(self):
        return {
            'mutant_id': self.mutant_id,
            'gene_id': self.gene_id,
            'gene_name': self.gene.name,
            'mutant_name': self.mutant_name,
            'phenotype': self.phenotype,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat()
        }


class SizeMetric(db.Model):
    __tablename__ = 'size_metrics'
    
    metric_id = db.Column(db.Integer, primary_key=True)
    mutant_id = db.Column(db.Integer, db.ForeignKey('mutants.mutant_id'), nullable=False)
    age_dpf = db.Column(db.Float)  # days post fertilization
    body_length = db.Column(db.Float)
    head_width = db.Column(db.Float)
    tail_length = db.Column(db.Float)
    weight_mg = db.Column(db.Float)
    sample_size = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'metric_id': self.metric_id,
            'mutant_id': self.mutant_id,
            'age_dpf': self.age_dpf,
            'body_length': self.body_length,
            'head_width': self.head_width,
            'tail_length': self.tail_length,
            'weight_mg': self.weight_mg,
            'sample_size': self.sample_size
        }


class BehaviorData(db.Model):
    __tablename__ = 'behavior_data'
    
    behavior_id = db.Column(db.Integer, primary_key=True)
    mutant_id = db.Column(db.Integer, db.ForeignKey('mutants.mutant_id'), nullable=False)
    behavior_type = db.Column(db.String(50))  # e.g., 'swimming_speed', 'startle_response'
    time_point = db.Column(db.Float)  # time in seconds or minutes
    value = db.Column(db.Float)
    unit = db.Column(db.String(20))
    
    def to_dict(self):
        return {
            'behavior_id': self.behavior_id,
            'mutant_id': self.mutant_id,
            'behavior_type': self.behavior_type,
            'time_point': self.time_point,
            'value': self.value,
            'unit': self.unit
        }