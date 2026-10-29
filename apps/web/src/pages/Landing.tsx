import { Link } from "react-router-dom";
import { DEFAULT_SAMPLE, SAMPLE_GROUPS, SAMPLES } from "../samples";

/* Nội dung trang lấy từ GAPMATE_Project_Brief_V1.2 (EXE101) và PMF Canvas.
   Tính năng thuộc Giai đoạn 2 (Mock Interview, Mentor 1-1, Master Profile,
   cổng việc làm) luôn được gắn nhãn "Sắp ra mắt" — bản demo hiện tại chỉ có
   phân tích CV ↔ JD. */

const MARKET_STATS: { value: string; label: string; source: string }[] = [
  {
    value: ">65%",
    label:
      "nhà tuyển dụng cho biết thách thức lớn nhất khi tuyển người mới tốt nghiệp là sự “lệch pha” giữa năng lực học thuật và yêu cầu thực tế",
    source: "Báo cáo thị trường tuyển dụng TopCV",
  },
  {
    value: "92,57%",
    label: "sinh viên gặp khó khăn khi thể hiện năng lực của mình trong CV",
    source: "Khảo sát của GAPMATE",
  },
  {
    value: "71,47%",
    label:
      "sinh viên tự đánh giá kỹ năng chuyên ngành của bản thân ở mức trung bình hoặc yếu",
    source: "Khảo sát của GAPMATE",
  },
];

const PAINS: { title: string; body: string }[] = [
  {
    title: "Mất phương hướng nghề nghiệp",
    body: "Không rõ bản thân mạnh ở đâu, phù hợp với vị trí nào và lộ trình phát triển của ngành ra sao.",
  },
  {
    title: "Không biết mình đang thiếu gì",
    body: "Không đo được khoảng cách giữa năng lực hiện tại và yêu cầu tuyển dụng, nên học lan man, thiếu trọng tâm.",
  },
  {
    title: "CV viết chung chung",
    body: "CV không bám sát JD, không làm nổi bật được kỹ năng và dự án phù hợp với từng vị trí cụ thể.",
  },
  {
    title: "Thiếu phản xạ phỏng vấn",
    body: "Ít cơ hội cọ xát, lúng túng khi diễn đạt và chưa nắm được kỳ vọng của người phỏng vấn.",
  },
  {
    title: "Khó tìm được Mentor chất lượng",
    body: "Người đi trước trong ngành khó tiếp cận, còn dịch vụ cố vấn hiện có thường quá đắt với sinh viên.",
  },
  {
    title: "Rơi vào “hố đen tuyển dụng”",
    body: "Nộp hồ sơ đại trà nhưng tỉ lệ phản hồi thấp. Vấn đề nằm ở mức độ phù hợp của từng hồ sơ với từng JD, không nằm ở số lượng.",
  },
];

const USPS: { title: string; body: string }[] = [
  {
    title: "Đánh giá theo tiêu chí của nhà tuyển dụng",
    body: "Không chỉ chấm điểm CV: GAPMATE chỉ ra bạn thiếu gì so với một vị trí cụ thể. Bộ tiêu chí do chính người làm tuyển dụng xây dựng và cập nhật cho từng ngành — AI không tự đặt tiêu chí.",
  },
  {
    title: "Hành trình chuẩn bị khép kín",
    body: "Chẩn đoán khoảng cách kỹ năng → luyện tập → nhận phản hồi từ người thật → kết nối cơ hội việc làm, trong một luồng duy nhất. Tiến bộ được đo bằng điểm tương thích với JD trước và sau lộ trình.",
  },
  {
    title: "Mentor 1-1 với giá sinh viên",
    body: "AI đảm nhận phần luyện lặp lại 24/7, Mentor tập trung vào phần AI không làm được: phong thái, tình huống thực tế và định hướng. Nhờ vậy chi phí mỗi buổi Mentor thấp hơn đáng kể so với dịch vụ cố vấn đơn lẻ trên thị trường — ở mức sinh viên chi trả được.",
  },
];

const FEATURES: { title: string; body: string; icon: React.ReactNode }[] = [
  {
    title: "Chấm điểm tương thích CV ↔ JD",
    body: "Điểm tổng cùng các điểm thành phần (kỹ năng, kinh nghiệm, học vấn, từ khóa). Mỗi kỹ năng khớp đều truy vết về bằng chứng cụ thể trong CV.",
    icon: (
      <>
        <circle cx="12" cy="12" r="9" />
        <circle cx="12" cy="12" r="5" />
        <circle cx="12" cy="12" r="1" fill="currentColor" />
      </>
    ),
  },
  {
    title: "Kiểm tra ATS & gợi ý sửa",
    body: "Rà soát khả năng đọc máy, cấu trúc và độ phủ từ khóa của CV. Mỗi lỗi đều có mức độ nghiêm trọng, cách sửa cụ thể và điểm ATS dự kiến sau khi sửa.",
    icon: (
      <>
        <path d="M12 3l7 2.8V11c0 4.6-3 7.7-7 9.2C8 18.7 5 15.6 5 11V5.8L12 3z" />
        <path d="M9 11.5l2.2 2.2L15.5 9.5" />
      </>
    ),
  },
  {
    title: "Lộ trình bù kỹ năng",
    body: "Các kỹ năng còn thiếu được xếp mức ưu tiên P0–P2 và dựng thành lộ trình theo từng giai đoạn, vừa với số giờ học mỗi tuần của bạn.",
    icon: (
      <>
        <path d="M5 19v-6a2 2 0 0 1 2-2h4a2 2 0 0 0 2-2V5" />
        <circle cx="5" cy="19" r="2" />
        <circle cx="17" cy="5" r="2" />
      </>
    ),
  },
  {
    title: "Gợi ý khóa học theo kỹ năng thiếu",
    body: "Khóa học được ghép đúng vào từng khoảng trống kỹ năng, kèm lý do được chọn — để lộ trình kết thúc bằng việc bạn bắt đầu học được ngay.",
    icon: (
      <>
        <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5v-15z" />
        <path d="M4 18V5.5" />
        <path d="M20 18H6.5A2.5 2.5 0 0 0 4 20.5" />
        <path d="M9 7.5h7" />
      </>
    ),
  },
];

const STEPS: { title: string; body: string }[] = [
  {
    title: "Dán CV và JD mục tiêu",
    body: "Hoặc nạp một trong các mẫu có sẵn để xem báo cáo đầy đủ chỉ với một cú bấm. Hỗ trợ CV/JD tiếng Việt, tiếng Anh và trộn cả hai.",
  },
  {
    title: "Nhận báo cáo có giải thích rõ ràng",
    body: "Điểm tương thích, lỗi ATS kèm cách sửa, gợi ý viết lại CV và danh sách kỹ năng thiếu theo mức ưu tiên — mọi điểm số đều có bằng chứng đi kèm.",
  },
  {
    title: "Lấp đầy khoảng trống",
    body: "Học theo lộ trình và các khóa học đã được ghép sẵn, rồi phân tích lại để thấy điểm số thay đổi.",
  },
];

const JOURNEY: { title: string; body: string; live: boolean }[] = [
  {
    title: "Hoàn thiện hồ sơ & AI tư vấn",
    body: "Phân tích CV theo từng JD mục tiêu, theo bộ tiêu chí chấm của từng ngành.",
    live: true,
  },
  {
    title: "Luyện phỏng vấn với AI 24/7",
    body: "Rèn phản xạ với câu hỏi chuyên môn và tình huống theo vị trí, nhận báo cáo phân tích ngay sau buổi luyện.",
    live: false,
  },
  {
    title: "Phỏng vấn thử 1-1 với Mentor",
    body: "Mô phỏng phỏng vấn thật với người đi trước trong ngành, nhận nhận xét chuyên môn và tư vấn định hướng.",
    live: false,
  },
  {
    title: "Bổ trợ kỹ năng qua Webinar & Workshop",
    body: "Chuỗi chia sẻ miễn phí về thị trường lao động, xu hướng ngành nghề và kinh nghiệm tuyển dụng.",
    live: false,
  },
  {
    title: "Tiếp cận doanh nghiệp liên kết",
    body: "Ứng viên hoàn thiện tốt hồ sơ và lộ trình được ưu tiên giới thiệu tới doanh nghiệp đối tác (khi ứng viên đồng ý chia sẻ hồ sơ).",
    live: false,
  },
];

const PRINCIPLES: { title: string; body: string }[] = [
  {
    title: "Không “thổi phồng” hồ sơ",
    body: "AI chỉ diễn đạt lại những gì bạn thật sự đã làm — không tự thêm kỹ năng, số liệu hay kinh nghiệm không có thật.",
  },
  {
    title: "Tiêu chí minh bạch",
    body: "Mọi điểm số đều truy vết được về bằng chứng trong CV và JD, theo bộ tiêu chí do người làm tuyển dụng soạn cho từng ngành.",
  },
  {
    title: "Tôn trọng dữ liệu cá nhân",
    body: "CV chỉ được xử lý khi bạn đồng ý; bạn có quyền xóa hồ sơ bất cứ lúc nào, và dữ liệu của bạn không bị dùng để huấn luyện AI.",
  },
  {
    title: "Song ngữ Việt – Anh",
    body: "CV và JD tiếng Việt, tiếng Anh hay trộn cả hai đều được phân tích như nhau.",
  },
];

function Icon({ children }: { children: React.ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-6 w-6"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

function ReportPreview() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xl shadow-indigo-100">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-800">Báo cáo mẫu</p>
        <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-500">
          Frontend Engineer · Tiếng Việt
        </span>
      </div>

      <div className="mt-5 flex items-center gap-5">
        <div className="flex h-24 w-24 shrink-0 flex-col items-center justify-center rounded-full border-4 border-indigo-500">
          <span className="text-2xl font-bold text-indigo-600">64</span>
          <span className="text-xs text-slate-500">/ 100 điểm</span>
        </div>
        <div className="min-w-0 space-y-2 text-sm">
          <p className="flex flex-wrap items-center gap-2">
            <span className="font-medium text-slate-700">Điểm ATS</span>
            <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 font-medium text-emerald-700">
              58 → 81 sau khi sửa
            </span>
          </p>
          <p className="text-slate-500">
            Phát hiện 2 lỗi ATS nghiêm trọng, mỗi lỗi đều có cách sửa cụ thể.
          </p>
        </div>
      </div>

      <div className="mt-5 border-t border-slate-100 pt-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          Kỹ năng cần bổ sung trước tiên
        </p>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {["TypeScript", "Testing"].map((skill) => (
            <span
              key={skill}
              className="rounded bg-rose-100 px-2 py-0.5 font-mono text-xs text-rose-700"
            >
              {skill}
            </span>
          ))}
          <span className="rounded bg-indigo-100 px-2 py-0.5 text-xs text-indigo-700">
            Lộ trình 90 ngày · 4 khóa học được ghép sẵn
          </span>
        </div>
      </div>
    </div>
  );
}

export default function Landing() {
  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-b from-indigo-50 via-white to-slate-50">
        <div className="mx-auto grid max-w-6xl items-center gap-10 px-6 pb-14 pt-14 lg:grid-cols-2 lg:pt-20">
          <div className="animate-fade-up">
            <span className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-white px-3 py-1 text-xs font-medium text-indigo-700">
              Dành cho sinh viên năm 3–4 & fresher · IT · Marketing · Quản trị
              kinh doanh
            </span>
            <h1 className="mt-5 text-4xl font-bold leading-tight tracking-tight text-slate-900 sm:text-5xl">
              Biết mình <span className="text-indigo-600">thiếu gì</span> —
              trước khi nhà tuyển dụng nói ra.
            </h1>
            <p className="mt-5 max-w-xl text-lg text-slate-600">
              GAPMATE đối chiếu CV của bạn với JD mục tiêu, chỉ rõ khoảng cách
              kỹ năng theo bộ tiêu chí do chính người làm tuyển dụng xây dựng
              cho từng ngành, rồi đưa ra lộ trình để bạn lấp đầy khoảng cách đó.
            </p>
            <p className="mt-3 max-w-xl text-sm text-slate-500">
              Cái tên nói lên tất cả: <strong>Gap</strong> là khoảng trống kỹ
              năng, kinh nghiệm bạn còn thiếu so với thị trường;{" "}
              <strong>Mate</strong> là người bạn đồng hành thẳng thắn chỉ ra
              điều còn thiếu và cùng bạn lấp đầy nó.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/analyze"
                className="rounded-lg bg-indigo-600 px-5 py-3 font-medium text-white shadow-sm transition hover:bg-indigo-500"
              >
                Chấm CV miễn phí ngay →
              </Link>
              <Link
                to={`/analyze?sample=${DEFAULT_SAMPLE.id}`}
                className="rounded-lg border border-slate-300 bg-white px-5 py-3 font-medium text-slate-700 transition hover:bg-slate-100"
              >
                Xem báo cáo mẫu
              </Link>
            </div>
          </div>
          <div className="animate-fade-up lg:pl-6">
            <ReportPreview />
            <p className="mt-3 text-center text-xs text-slate-400">
              Minh họa theo kịch bản demo có sẵn trong hệ thống.
            </p>
          </div>
        </div>

        {/* Market stats */}
        <div className="border-t border-indigo-100/70">
          <div className="mx-auto grid max-w-6xl gap-8 px-6 py-10 sm:grid-cols-3">
            {MARKET_STATS.map((s) => (
              <div key={s.value}>
                <p className="text-3xl font-bold text-indigo-600">{s.value}</p>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {s.label}
                </p>
                <p className="mt-1 text-xs text-slate-400">Nguồn: {s.source}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pain points */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-2xl font-bold text-slate-900">
          Nộp CV mãi không ai gọi — vấn đề thường không nằm ở bạn
        </h2>
        <p className="mt-2 max-w-2xl text-slate-600">
          Rất nhiều sinh viên chăm chỉ vẫn trượt từ vòng hồ sơ. Đây là những
          điều GAPMATE nghe được lặp đi lặp lại khi khảo sát và phỏng vấn sinh
          viên chuẩn bị đi thực tập:
        </p>
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {PAINS.map((p) => (
            <article
              key={p.title}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <h3 className="font-semibold text-slate-900">{p.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                {p.body}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* USPs */}
      <section className="border-y border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <h2 className="text-2xl font-bold text-slate-900">
            Khác biệt của GAPMATE
          </h2>
          <p className="mt-2 max-w-2xl text-slate-600">
            Các công cụ hiện nay phần lớn dừng ở việc tạo CV và chấm điểm chung.
            GAPMATE đi tiếp ba bước nữa:
          </p>
          <div className="mt-8 grid gap-5 lg:grid-cols-3">
            {USPS.map((u, i) => (
              <article
                key={u.title}
                className="rounded-2xl border border-indigo-100 bg-indigo-50/50 p-6"
              >
                <span className="text-sm font-bold uppercase tracking-wide text-indigo-500">
                  USP {i + 1}
                </span>
                <h3 className="mt-2 font-semibold text-slate-900">{u.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {u.body}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Features — live in the demo */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              Trải nghiệm ngay với bản demo
            </h2>
            <p className="mt-2 max-w-2xl text-slate-600">
              Một báo cáo, bốn câu trả lời: có nên ứng tuyển không, CV có qua
              được vòng lọc ATS không, cần học thêm gì, và học ở đâu.
            </p>
          </div>
          <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">
            Đang chạy thật
          </span>
        </div>
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f) => (
            <article
              key={f.title}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md"
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                <Icon>{f.icon}</Icon>
              </div>
              <h3 className="mt-4 font-semibold text-slate-900">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">
                {f.body}
              </p>
            </article>
          ))}
        </div>
        <p className="mt-6 text-sm text-slate-500">
          Kho dữ liệu hiện tại: taxonomy {191} kỹ năng · catalog {30} khóa học ·{" "}
          {SAMPLES.length} cặp CV–JD mẫu thuộc {SAMPLE_GROUPS.length} nhóm
          ngành.
        </p>
      </section>

      {/* How it works */}
      <section className="border-y border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <h2 className="text-2xl font-bold text-slate-900">Cách hoạt động</h2>
          <ol className="mt-8 grid gap-8 md:grid-cols-3">
            {STEPS.map((step, i) => (
              <li key={step.title}>
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-600 font-semibold text-white">
                  {i + 1}
                </span>
                <h3 className="mt-4 font-semibold text-slate-900">
                  {step.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {step.body}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* End-to-end journey */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-2xl font-bold text-slate-900">
          Hành trình GAPMATE — không chỉ dừng ở một bản báo cáo
        </h2>
        <p className="mt-2 max-w-2xl text-slate-600">
          Chẩn đoán chỉ là bước đầu. GAPMATE đang xây dựng hành trình khép kín
          từ lúc hoàn thiện hồ sơ tới khi bạn tiếp cận doanh nghiệp — các bước
          thuộc Giai đoạn 2 được gắn nhãn rõ ràng:
        </p>
        <ol className="mt-8 space-y-4">
          {JOURNEY.map((j, i) => (
            <li
              key={j.title}
              className="flex flex-col gap-2 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:flex-row sm:items-start sm:gap-4"
            >
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-indigo-600 font-semibold text-white">
                {i + 1}
              </span>
              <div className="min-w-0 flex-1">
                <h3 className="font-semibold text-slate-900">{j.title}</h3>
                <p className="mt-1 text-sm leading-relaxed text-slate-600">
                  {j.body}
                </p>
              </div>
              {j.live ? (
                <span className="shrink-0 rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">
                  Dùng ngay ở bản demo
                </span>
              ) : (
                <span className="shrink-0 rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">
                  Sắp ra mắt · Giai đoạn 2
                </span>
              )}
            </li>
          ))}
        </ol>
      </section>

      {/* Pricing — chua cong bo, san pham dang o giai doan demo */}
      <section className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <div className="flex flex-col items-start gap-6 rounded-3xl border-2 border-dashed border-indigo-200 bg-indigo-50/50 px-6 py-10 sm:px-10 lg:flex-row lg:items-center">
            <div className="min-w-0 flex-1">
              <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">
                Coming soon
              </span>
              <h2 className="mt-4 text-2xl font-bold text-slate-900">
                Gói dịch vụ & bảng giá — sắp công bố
              </h2>
              <p className="mt-2 max-w-2xl text-slate-600">
                GAPMATE hiện đang ở giai đoạn demo để kiểm chứng trải nghiệm và
                chất lượng phân tích. Các gói dịch vụ AI và Mentor 1-1 đang được
                hoàn thiện và sẽ được công bố khi sản phẩm ra mắt chính thức.
                Trong thời gian này, bạn có thể dùng miễn phí toàn bộ tính năng
                phân tích CV ↔ JD ở bản demo.
              </p>
            </div>
            <Link
              to="/analyze"
              className="shrink-0 rounded-lg bg-indigo-600 px-5 py-3 font-medium text-white shadow-sm transition hover:bg-indigo-500"
            >
              Dùng thử bản demo miễn phí →
            </Link>
          </div>
        </div>
      </section>

      {/* Samples by industry */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-2xl font-bold text-slate-900">
          Không chỉ dành cho ngành IT
        </h2>
        <p className="mt-2 max-w-2xl text-slate-600">
          Bộ mẫu CV–JD có sẵn bao phủ {SAMPLE_GROUPS.length} nhóm ngành. Chọn
          một ngành để mở trang phân tích với CV và JD mẫu đã được nạp sẵn:
        </p>
        <div className="mt-6 flex flex-wrap gap-2">
          {SAMPLE_GROUPS.map((group) => (
            <Link
              key={group.industry}
              to={`/analyze?sample=${group.samples[0].id}`}
              className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 transition hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700"
            >
              {group.industry}
              <span className="ml-1.5 text-xs text-slate-400">
                {group.samples.length}
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* Principles */}
      <section className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <h2 className="text-2xl font-bold text-slate-900">
            Nguyên tắc để bạn yên tâm tin tưởng
          </h2>
          <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {PRINCIPLES.map((p) => (
              <article key={p.title}>
                <h3 className="flex items-center gap-2 font-semibold text-slate-900">
                  <span className="text-emerald-500" aria-hidden="true">
                    ✓
                  </span>
                  {p.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">
                  {p.body}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="rounded-3xl bg-indigo-600 px-6 py-12 text-center sm:px-12">
          <h2 className="text-2xl font-bold text-white sm:text-3xl">
            Biết mình thiếu gì — trước khi nhà tuyển dụng nói ra
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-indigo-100">
            Dán CV và JD mục tiêu của bạn vào, báo cáo đầy đủ chỉ sau một cú
            bấm.
          </p>
          <Link
            to="/analyze"
            className="mt-8 inline-block rounded-lg bg-white px-6 py-3 font-medium text-indigo-700 shadow-sm transition hover:bg-indigo-50"
          >
            Bắt đầu phân tích →
          </Link>
        </div>
      </section>
    </div>
  );
}
