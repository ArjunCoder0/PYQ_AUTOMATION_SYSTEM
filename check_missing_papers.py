import sqlite3

conn = sqlite3.connect('backend/pyq_system.db')
cursor = conn.cursor()

# Get all branch-semester combinations
cursor.execute('''
    SELECT branch, semester, COUNT(*) as count
    FROM pyq_files
    GROUP BY branch, semester
    ORDER BY branch, semester
''')

results = cursor.fetchall()

# Create a matrix showing which combinations exist
branches = ['CSE', 'ME', 'CE', 'EE', 'ECE']
semesters = list(range(1, 9))

print("=" * 100)
print(" " * 30 + "BRANCH-SEMESTER COVERAGE MATRIX")
print("=" * 100)
print("\nLegend: ✅ = Has papers | ❌ = Missing papers | Number = Paper count\n")

# Create matrix
matrix = {}
for branch in branches:
    matrix[branch] = {sem: 0 for sem in semesters}

for branch, semester, count in results:
    if branch in matrix:
        matrix[branch][semester] = count

# Print header
print(f"{'Branch':<10}", end="")
for sem in semesters:
    print(f"Sem {sem:<5}", end="")
print()
print("-" * 100)

# Print each branch
for branch in branches:
    print(f"{branch:<10}", end="")
    for sem in semesters:
        count = matrix[branch][sem]
        if count > 0:
            print(f"✅ {count:<5}", end="")
        else:
            print(f"❌ 0    ", end="")
    print()

print("\n" + "=" * 100)
print("MISSING COMBINATIONS (Branch + Semester with 0 papers)")
print("=" * 100)

missing = []
for branch in branches:
    for sem in semesters:
        if matrix[branch][sem] == 0:
            missing.append(f"{branch} Semester {sem}")

if missing:
    print("\n⚠️  The following branch-semester combinations have NO papers:\n")
    for item in missing:
        print(f"  • {item}")
    print(f"\nTotal missing: {len(missing)} out of {len(branches) * len(semesters)} possible combinations")
else:
    print("\n✅ All branch-semester combinations have papers!")

# Summary by branch
print("\n" + "=" * 100)
print("SUMMARY BY BRANCH")
print("=" * 100)

for branch in branches:
    total = sum(matrix[branch].values())
    sems_with_papers = sum(1 for count in matrix[branch].values() if count > 0)
    print(f"\n{branch}:")
    print(f"  Total papers: {total}")
    print(f"  Semesters covered: {sems_with_papers}/8")
    print(f"  Missing semesters: ", end="")
    missing_sems = [sem for sem in semesters if matrix[branch][sem] == 0]
    if missing_sems:
        print(", ".join(map(str, missing_sems)))
    else:
        print("None ✅")

# Overall statistics
print("\n" + "=" * 100)
print("OVERALL STATISTICS")
print("=" * 100)

cursor.execute('SELECT COUNT(*) FROM pyq_files')
total_papers = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(DISTINCT branch) FROM pyq_files')
branches_with_papers = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(DISTINCT semester) FROM pyq_files')
semesters_with_papers = cursor.fetchone()[0]

print(f"\nTotal papers in database: {total_papers}")
print(f"Branches with papers: {branches_with_papers}/5")
print(f"Semesters with papers: {semesters_with_papers}/8")
print(f"Coverage: {len(results)}/{len(branches) * len(semesters)} branch-semester combinations")

conn.close()
