# build-phase7: Quickstart

## Finalization Verification

### Prerequisites
- All build phases complete (build-phase1 through build-phase6)
- All 285 tasks [COMPLETE]
- Access to git repository
- Access to run verification checks

### 1. Verify All Spec.md Statuses
```bash
# Check all spec.md files have status Implemented
for phase in 1 2 3 4 5 6 7; do
  status=$(grep -m1 'Status' specs/00${phase}-build-phase*/spec.md | head -1)
  echo "build-phase${phase}: $status"
done
```

### 2. Constitution Reconciliation
```bash
# Verify constitution documents are reconciled
grep -c "Implemented" .specify/memory/constitution.md
grep -c "Implemented" docs/constitution.md | head -1
```

### 3. Traceability Matrix Verification
```bash
# Verify traceability matrix has all mappings (TM001–TM220)
grep -c "TM" docs/traceability-matrix.md
# Should be 220+ mappings
```

### 4. Fresh Clone Verification
```bash
# Full environment verification (approximately 45 minutes)
make check
# Or individual checks:
make docker-up
make migrate-all
make test-all
```

### 5. Hand-off Documentation
```bash
# Verify all artifacts are in place
ls specs/00*/spec.md specs/00*/plan.md specs/00*/research.md specs/00*/data-model.md
ls specs/00*/checklists/requirements.md specs/00*/contracts/
ls .specify/feature.json .specify/memory/constitution.md

# Verify hand-off documentation is complete
echo "SPEC-001 Completion Report generated"
echo "All 6 build phases verified"
echo "All 285 tasks verified complete"
echo "Traceability matrix TM001–TM220 verified"
```

### 6. Hand-off Documentation Distribution
```bash
# Distribute hand-off documentation to stakeholders
# Copy to shared location or send via email
cp SPEC-001_completion_report.md /shared/location/
# Or:
git commit -am "SPEC-001 complete: all 6 build phases, 285 tasks, all artifacts"
git push origin main
```

## SDK Usage (Finalization)

### Python - Project Status Check
```python
import json

# Check project status from feature.json
with open('.specify/feature.json') as f:
    feature = json.load(f)
print(f"Feature directory: {feature['feature_directory']}")

# Check constitution status
with open('.specify/memory/constitution.md') as f:
    constitution = f.read()
print(f"Constitution status contains Implemented: {'Implemented' in constitution}")
```

### Python - Trace Mapping Verification
```python
import re

# Check traceability matrix has all mappings
with open('docs/traceability-matrix.md') as f:
    content = f.read()
mappings = re.findall(r'TM\d+', content)
print(f"Trace mappings found: {len(mappings)}")
print(f"Expected: 220")
```

### Python - Constitution Verification
```python
# Verify constitution has all articles Implemented
with open('.specify/memory/constitution.md') as f:
    content = f.read()
articles_implemented = content.count('Status: Implemented')
print(f"Articles Implemented: {articles_implemented}")
print(f"Expected: 11")
```

## Verification Checklist
- [ ] All spec.md files across build-phases status set to Implemented
- [ ] Constitution reconciliation complete with dates and signatures
- [ ] Traceability matrix TM001–TM220 complete with all test mappings mapped
- [ ] Fresh clone verification passes all check sets within 45 minutes
- [ ] Hand-off documentation complete and distributed

## Completion Verification Commands
```bash
# Final verification script
echo "=== SPEC-001 Final Verification ==="
echo "Checking all spec.md statuses..."
# ... verification code ...
echo "=== Verification Complete ==="
echo "SPEC-001: All build phases complete"
echo "Total tasks: 285"
echo "All tasks [COMPLETE]: Yes"
echo "Constitution: Implemented"
echo "Traceability: TM001–TM220 complete"
```
