from decimal import Decimal
from engine import validate_against_tenant_blueprint, BlueprintValidationError

# --- TENANT A: Strict STEM Academy ---
# Uses: Quiz (20 marks) + Midterm Lab (30 marks) + Final Exam (50 marks) = 100 max
stem_blueprint = [
    {"key": "quiz", "label": "Weekly Quiz", "max_score": 20},
    {"key": "lab", "label": "Midterm Practical Lab", "max_score": 30},
    {"key": "exam", "label": "Final Comprehensive Exam", "max_score": 50},
]

# --- TENANT B: Liberal Arts Institute ---
# Uses: Attendance (10 marks) + Essay Project (40 marks) + Presentation (50 marks) = 100 max
arts_blueprint = [
    {"key": "attendance", "label": "Class Attendance", "max_score": 10},
    {"key": "essay", "label": "Research Essay", "max_score": 40},
    {"key": "presentation", "label": "Oral Presentation", "max_score": 50},
]

if __name__ == "__main__":
    print("___ Testing Tenant A (STEM Academy) ___")
    student_a_scores = {"quiz": 18.5, "lab": 27.0, "exam": 42.5}
    try:
        total_a = validate_against_tenant_blueprint(stem_blueprint, student_a_scores)
        print(f"Success! Student A Total Score: {total_a} / 100\n")
    except BlueprintValidationError as e:
        print(f"Validation Failed: {e}\n")

    print("___ Testing Tenant B (Liberal Arts Institute) ___")
    student_b_scores = {"attendance": 10, "essay": 35, "presentation": 48}
    try:
        total_b = validate_against_tenant_blueprint(arts_blueprint, student_b_scores)
        print(f"Success! Student B Total Score: {total_b} / 100\n")
    except BlueprintValidationError as e:
        print(f"Validation Failed: {e}\n")

    print("___ Testing Validation Error Trap (Over Max Score) ___")
    bad_scores = {"quiz": 25.0, "lab": 20.0, "exam": 40.0} # Quiz max is 20!
    try:
        validate_against_tenant_blueprint(stem_blueprint, bad_scores)
    except BlueprintValidationError as e:
        print(f"Caught Expected Error: {e}")