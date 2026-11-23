# ASF 모의 데이터 파이프라인

이 프로젝트는 2024년 업무에서 다뤘던 후보 수집, 중복 검사, 분류, 결과 저장을 일반화한 **독립 구현**입니다. 실제 웹사이트를 접속하거나 원래 사용했던 규칙을 재현하지 않습니다.

\`\`\`mermaid
flowchart LR
    A[가상 후보 JSON] --> B[필드 검증]
    B --> C[예시 분류 규칙]
    C --> D[SQLite 중복 방지 UPSERT]
    D --> E[수동 검토 대상]
    D --> F[CSV 후보 내보내기]
    D --> G[변경 및 분류 이력]
\`\`\`

## 실행

\`\`\`bash
python run_pipeline.py --db synthetic_demo.sqlite --export candidate_export.csv
python run_pipeline.py --db synthetic_demo.sqlite --export candidate_export.csv
python -m unittest discover -s tests -v
\`\`\`

같은 데이터를 두 번 넣어도 후보는 중복되지 않습니다. 가상 데이터만 사용합니다. 분류 규칙, 팔로워 기준, 계정 이름과 수치는 교육용으로 만든 값이며 실무 적용 기준과 다릅니다.
