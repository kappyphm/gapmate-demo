import type { SamplePair } from "./types";

/**
 * Deliberately messy, realistic CVs/JDs (synthetic, no PII) to exercise edge cases:
 * run-on prose instead of bullets, weak verbs, missing metrics, mixed date formats,
 * crammed keyword dumps and unexplained acronyms.
 */
export const EDGE_SAMPLES: SamplePair[] = [
  {
    id: "edge-fresher-messy-vi",
    label: "Fresher lộn xộn, không bullet (VI)",
    industry: "Edge cases",
    language: "vi",
    cv: `Nguyễn Văn Tèo
em là sinh viên mới ra trường, thích làm web
sđt 0912 xxx xxx (có zalo), email teo.nguyen@example.com
học cntt ở đại học demo, 2019-2023, bằng khá

kinh nghiệm
thực tập ở công ty nhỏ, được giao làm web bằng wordpress xong chuyển sang react,
có sửa vài lỗi giao diện với hỗ trợ anh chị trong nhóm, đôi khi viết tài liệu, tham gia họp
đồ án tốt nghiệp làm app quản lý sinh viên dùng react với nodejs

kỹ năng: react, javascript, css, html, biết chút python, tiếng anh đọc tài liệu ok`,
    jd: `# Frontend Developer (React)

**Công ty:** Demo Studio
**Địa điểm:** Hà Nội
**Trình độ:** Fresher – Junior

## Mô tả công việc

Tham gia phát triển giao diện web cho sản phẩm SaaS cùng team Design và Backend.

## Yêu cầu bắt buộc

- Nắm chắc JavaScript và React.
- Biết HTML, CSS và Tailwind CSS.
- Sử dụng được Git.
- Tiếng Anh đọc hiểu tài liệu.

## Ưu tiên (Nice to have)

- Biết TypeScript.
- Kinh nghiệm với Next.js.
- Hiểu REST API.`,
  },
  {
    id: "edge-fresher-messy-en",
    label: "Fresher messy, no bullets (EN)",
    industry: "Edge cases",
    language: "en",
    cv: `Teo Nguyen
i am a fresh grad who likes building websites
ph 0912 xxx xxx, mail teo.nguyen@example.com
studied it at demo university 2019-2023, fair grades

experience
interned at a small shop, was told to make a site with wordpress then moved to react,
fixed some ui bugs and helped the team, sometimes wrote docs, joined meetings
final project was a student manager app with react and nodejs

skills: react, javascript, css, html, a bit of python, english for docs`,
    jd: `# Frontend Developer (React)

**Company:** Demo Studio
**Location:** Hanoi
**Level:** Fresher – Junior

## About the role

Build web interfaces for a SaaS product with the Design and Backend teams.

## Required

- Solid JavaScript and React.
- HTML, CSS and Tailwind CSS.
- Comfortable with Git.
- English for reading documentation.

## Nice to have

- TypeScript.
- Experience with Next.js.
- Understanding of REST APIs.`,
  },
  {
    id: "edge-switch-to-data-vi",
    label: "Chuyển ngành sang Data (VI)",
    industry: "Edge cases",
    language: "vi",
    cv: `# Phạm Thu Hà

- Email: ha.pham@example.com
- Điện thoại: 0900 000 003
- Địa điểm: Đà Nẵng, Việt Nam

## Giới thiệu

Mình làm sales/marketing 4 năm, gần đây tự học phân tích dữ liệu nên muốn chuyển hẳn
sang data. Thích làm việc với con số, hay tự lập báo cáo và tối ưu quảng cáo cho công ty cũ.

## Kinh nghiệm

### Công ty Demo Media — Chuyên viên Marketing (2019 – 2023)
Mình phụ trách chạy quảng cáo facebook và google, theo dõi hiệu quả bằng excel,
làm báo cáo hằng tuần cho sếp, đôi khi viết sql để lấy dữ liệu từ database nội bộ,
phối hợp với team thiết kế để làm banner, và tham gia brainstorming ý tưởng chiến dịch.

### Trung tâm Demo — Nhân viên kinh doanh (2018 – 2019)
Tư vấn khách hàng, ghi nhận thông tin vào file excel, chốt hợp đồng.

## Kỹ năng

- Excel (pivot, hàm if/vlookup)
- SQL cơ bản
- Python: tự học cơ bản
- Tiếng Anh: giao tiếp ổn

## Học vấn

- Đại học Kinh tế Demo — Quản trị kinh doanh (2014 – 2018)`,
    jd: `# Data Analyst

**Công ty:** Demo Analytics
**Trình độ:** Junior

## Yêu cầu bắt buộc

- Thành thạo SQL.
- Python cho phân tích dữ liệu (pandas).
- Power BI để làm dashboard.
- Excel nâng cao.
- Kỹ năng trình bày và giao tiếp tốt.

## Ưu tiên (Nice to have)

- Kinh nghiệm với Tableau.
- Hiểu về A/B testing.`,
  },
  {
    id: "edge-keyword-stuffed-en",
    label: "Nhồi keyword, lạm dụng viết tắt (EN)",
    industry: "Edge cases",
    language: "en",
    cv: `# Alex Demo

- Email: alex.demo@example.com
- Phone: 0900 000 004
- Location: Remote

## Profile

Passionate ninja rockstar developer and 10x engineer. Results-driven, detail-oriented,
self-motivated team player with a can-do attitude.

## Skills

AWS, Azure, GCP, Docker, Kubernetes, Terraform, React, Angular, Vue, Svelte, Node.js,
Python, Go, Java, Rust, PostgreSQL, MySQL, MongoDB, Redis, Kafka, RabbitMQ, GraphQL,
REST, gRPC, CI/CD, TDD, BDD, Agile, Scrum, Kanban, Machine Learning, Blockchain, DevOps.

## Experience

### Various Companies — Software Engineer
Did various tasks as needed. Worked on many projects across the stack. Helped where needed.
"Rockstar" contributor. Other duties as assigned.`,
    jd: `# Backend Engineer

**Company:** Demo Cloud
**Level:** Middle

## Required

- Strong Python and PostgreSQL.
- Experience with REST API design.
- Docker in daily work.
- Understanding of CI/CD.

## Nice to have

- Kafka.
- Kubernetes.`,
  },
  {
    id: "edge-no-metrics-vi",
    label: "Động từ tốt nhưng thiếu số liệu (VI)",
    industry: "Edge cases",
    language: "vi",
    cv: `# Đỗ Minh Quân

- Email: quan.do@example.com
- Điện thoại: 0900 000 005
- Địa điểm: Hà Nội, Việt Nam
- GitHub: github.com/quan-demo

## Mục tiêu nghề nghiệp

Backend developer tập trung vào chất lượng code và hiệu năng hệ thống.

## Kỹ năng

- Ngôn ngữ: Python, SQL
- Framework: FastAPI, Django
- Cơ sở dữ liệu: PostgreSQL, Redis
- Công cụ: Docker, Git

## Kinh nghiệm làm việc

### Demo Tech — Backend Developer (2021 – nay)
- Thiết kế REST API bằng FastAPI cho hệ thống nội bộ.
- Triển khai Docker cho các service.
- Viết unit test cho các module quan trọng.
- Tối ưu truy vấn PostgreSQL.
- Phối hợp với frontend để tích hợp API.

## Học vấn

- Đại học Công nghệ Demo — Cử nhân CNTT (2017 – 2021)`,
    jd: `# Backend Developer

**Công ty:** Demo Tech
**Trình độ:** Middle

## Yêu cầu bắt buộc

- 3+ năm kinh nghiệm với Python.
- Thành thạo FastAPI hoặc Django.
- Kinh nghiệm PostgreSQL.
- Biết Docker.
- Viết test.`,
  },
  {
    id: "edge-overqualified-en",
    label: "Senior apply vị trí Junior (EN)",
    industry: "Edge cases",
    language: "en",
    cv: `# Morgan Demo

- Email: morgan.demo@example.com
- Phone: 0900 000 006
- Location: Ho Chi Minh City, Vietnam
- GitHub: github.com/morgan-demo

## Summary

Staff engineer with 12 years of experience leading platform teams and shipping distributed systems.

## Skills

- Languages: Go, Python, TypeScript, Rust
- Infrastructure: Kubernetes, Terraform, AWS, Docker
- Data: PostgreSQL, Redis, Kafka
- Practices: CI/CD, TDD, Agile

## Experience

### Big Cloud Co — Staff Engineer (2018 – Present)
- Led a team of 9 engineers building a multi-region platform.
- Cut infrastructure cost by 32% by re-architecting services.
- Owned CI/CD and on-call for 40+ microservices.
- Mentored 6 engineers, 3 promoted to senior.

### Mid Startup — Senior Backend Engineer (2014 – 2018)
- Built event-driven services with Kafka handling 50k events/s.
- Introduced TDD, raising coverage from 40% to 85%.

## Education

- Demo University — B.Sc. Computer Science (2010 – 2014)`,
    jd: `# Junior Backend Developer

**Company:** Demo Startup
**Location:** Hanoi
**Level:** Junior (0–2 years)
**Employment:** Full-time

## About the role

Join a small team and help build REST APIs for our first product.

## Required

- 0–2 years of experience.
- Basic Python.
- Willingness to learn.

## Nice to have

- Any web framework experience.`,
  },
];
