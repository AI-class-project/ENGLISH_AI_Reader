// Mock data simulating toeic_pool.json loaded via backend API
// ToeicQuestionModel structure:
// type: "cloze" | "reading_single" | "reading_multi"
// category: "grammar" | "vocabulary" | "reading"
// For cloze: { id, type, category, passage, blank_index, options, answer, explanation }
// For reading: { id, type, category, passage, questions: [{id, stem, options, answer, explanation}] }

export const toeicPool = {
  cloze: [
    {
      id: "CL001",
      type: "cloze",
      category: "grammar",
      passage: "The new marketing campaign ______ launched next Monday after months of preparation.",
      blank_index: 4,
      options: { A: "will be", B: "has been", C: "was", D: "is being" },
      answer: "A",
      explanation: "Future passive voice 'will be + p.p.' is correct here since the event hasn't happened yet (next Monday).",
      difficulty: "medium",
      tags: ["passive voice", "future tense"]
    },
    {
      id: "CL002",
      type: "cloze",
      category: "vocabulary",
      passage: "The board of directors ______ a unanimous decision to expand operations into Southeast Asia.",
      blank_index: 4,
      options: { A: "did", B: "reached", C: "took", D: "made" },
      answer: "D",
      explanation: "'Made a decision' is the correct collocation in English.",
      difficulty: "easy",
      tags: ["collocation", "vocabulary"]
    },
    {
      id: "CL003",
      type: "cloze",
      category: "grammar",
      passage: "______ the project deadline, all team members worked overtime for the past two weeks.",
      blank_index: 0,
      options: { A: "Due to meet", B: "In order to meet", C: "So as meeting", D: "For meeting" },
      answer: "B",
      explanation: "'In order to + verb' expresses purpose. 'Due to' is followed by a noun, not an infinitive.",
      difficulty: "hard",
      tags: ["infinitive of purpose", "conjunctions"]
    },
    {
      id: "CL004",
      type: "cloze",
      category: "vocabulary",
      passage: "Please ______ your supervisor before submitting any documents to the client directly.",
      blank_index: 1,
      options: { A: "consult", B: "discuss", C: "advise", D: "suggest" },
      answer: "A",
      explanation: "'Consult your supervisor' means to seek advice from them. 'Discuss' requires an object after 'with'.",
      difficulty: "medium",
      tags: ["vocabulary", "workplace"]
    },
    {
      id: "CL005",
      type: "cloze",
      category: "grammar",
      passage: "The shipment, ______ was delayed by two weeks, finally arrived at the warehouse yesterday.",
      blank_index: 2,
      options: { A: "that", B: "which", C: "what", D: "who" },
      answer: "B",
      explanation: "Non-restrictive relative clause referring to a thing uses 'which', not 'that'.",
      difficulty: "medium",
      tags: ["relative clause", "grammar"]
    },
    {
      id: "CL006",
      type: "cloze",
      category: "vocabulary",
      passage: "The company has decided to ______ its annual budget by 15% to accommodate new hires.",
      blank_index: 5,
      options: { A: "increase", B: "augment", C: "expand", D: "raise" },
      answer: "A",
      explanation: "'Increase a budget' is the standard collocation in business English.",
      difficulty: "easy",
      tags: ["vocabulary", "finance"]
    },
    {
      id: "CL007",
      type: "cloze",
      category: "grammar",
      passage: "Had the manager reviewed the report thoroughly, she ______ the critical error in the data.",
      blank_index: 8,
      options: { A: "would catch", B: "would have caught", C: "had caught", D: "caught" },
      answer: "B",
      explanation: "Third conditional: 'Had + p.p. ... would have + p.p.' for unreal past situations.",
      difficulty: "hard",
      tags: ["conditional", "subjunctive"]
    },
    {
      id: "CL008",
      type: "cloze",
      category: "vocabulary",
      passage: "The new policy is ______ to reduce employee turnover and improve overall job satisfaction.",
      blank_index: 3,
      options: { A: "intended", B: "supposed", C: "designed", D: "aimed" },
      answer: "C",
      explanation: "'Designed to' is the most natural phrasing when referring to a policy created for a specific purpose.",
      difficulty: "medium",
      tags: ["vocabulary", "HR"]
    }
  ],
  reading: [
    {
      id: "RS001",
      type: "reading_single",
      category: "reading",
      difficulty: "medium",
      passage: `To: All Staff
From: Human Resources Department
Subject: Upcoming Office Relocation

We are pleased to announce that our company will be relocating to a new, state-of-the-art facility at 45 Innovation Drive, effective March 1st. The new office features open collaboration spaces, updated technology infrastructure, and an on-site cafeteria.

Employees are encouraged to begin packing personal items from their current workstations starting February 20th. Moving boxes will be provided by the facilities team and can be picked up from the main reception area.

Please note that parking arrangements at the new location differ from our current setup. A detailed parking guide will be distributed next week. For questions, contact HR at hr@company.com.`,
      questions: [
        {
          id: "RS001-Q1",
          stem: "What is the primary purpose of this memo?",
          options: {
            A: "To announce a company merger",
            B: "To inform employees about an office move",
            C: "To update parking regulations",
            D: "To introduce a new HR policy"
          },
          answer: "B",
          explanation: "The memo explicitly states 'our company will be relocating to a new facility', making B the correct answer."
        },
        {
          id: "RS001-Q2",
          stem: "When should employees start packing their belongings?",
          options: {
            A: "March 1st",
            B: "February 20th",
            C: "Next week",
            D: "Immediately"
          },
          answer: "B",
          explanation: "The memo states 'begin packing personal items from their current workstations starting February 20th'."
        },
        {
          id: "RS001-Q3",
          stem: "What information will be provided next week?",
          options: {
            A: "New office floor plans",
            B: "Moving box distribution schedule",
            C: "Parking details at the new location",
            D: "Cafeteria menu options"
          },
          answer: "C",
          explanation: "'A detailed parking guide will be distributed next week' is directly stated in the memo."
        }
      ]
    },
    {
      id: "RS002",
      type: "reading_single",
      category: "reading",
      difficulty: "hard",
      passage: `QUARTERLY FINANCIAL REPORT – Q3 SUMMARY

Nexgen Technologies reported a 23% increase in net revenue for Q3, reaching $4.2 billion compared to $3.4 billion in the same period last year. This growth was primarily driven by strong performance in the cloud services division, which saw a 41% year-over-year increase.

However, operating expenses also rose by 18%, largely due to significant investments in research and development as well as expanded sales operations in the Asia-Pacific region. Despite these costs, the company maintained a healthy operating margin of 19.4%.

CEO Sandra Kim stated that the company remains on track to meet its full-year guidance of $16 billion in revenue, with particular optimism about growth in the enterprise software segment in Q4.`,
      questions: [
        {
          id: "RS002-Q1",
          stem: "What was the primary driver of revenue growth in Q3?",
          options: {
            A: "Enterprise software sales",
            B: "Cloud services division",
            C: "Asia-Pacific expansion",
            D: "Cost reduction strategies"
          },
          answer: "B",
          explanation: "The report states growth 'was primarily driven by strong performance in the cloud services division'."
        },
        {
          id: "RS002-Q2",
          stem: "What does the CEO suggest about Q4?",
          options: {
            A: "Operating costs will decrease",
            B: "Revenue guidance will be revised downward",
            C: "Enterprise software is expected to grow",
            D: "Cloud services will slow down"
          },
          answer: "C",
          explanation: "CEO Kim expressed 'particular optimism about growth in the enterprise software segment in Q4'."
        }
      ]
    },
    {
      id: "RM001",
      type: "reading_multi",
      category: "reading",
      difficulty: "hard",
      passages: [
        {
          label: "Article A",
          text: `JOB POSTING – Senior Project Manager

Orion Consulting Group is seeking an experienced Senior Project Manager to join our rapidly growing team in Taipei. The ideal candidate will have a minimum of 7 years of project management experience, PMP certification, and demonstrated ability to manage cross-functional teams.

Responsibilities include overseeing project timelines, managing client relationships, and ensuring deliverables meet quality standards. Proficiency in project management software (e.g., MS Project, Jira) is required. Salary range: NT$120,000–NT$150,000 per month.

To apply, send your resume and cover letter to careers@orionconsulting.com by December 15th.`
        },
        {
          label: "Article B",
          text: `Email Correspondence:

From: Michael Chen <m.chen@email.com>
To: careers@orionconsulting.com
Subject: Application – Senior Project Manager

Dear Hiring Team,

I am writing to express my strong interest in the Senior Project Manager position advertised on your website. I hold a PMP certification and have 9 years of experience leading projects in the IT consulting industry, including several large-scale digital transformation initiatives across Southeast Asia.

Although I am currently based in Singapore, I am prepared to relocate to Taipei and am available to start from January 15th. I have attached my resume and a cover letter for your review.

I look forward to the opportunity to discuss how my background aligns with Orion's goals.

Sincerely,
Michael Chen`
        }
      ],
      questions: [
        {
          id: "RM001-Q1",
          stem: "Which requirement listed in the job posting does Michael Chen directly address in his email?",
          options: {
            A: "Proficiency in MS Project",
            B: "PMP Certification",
            C: "Experience managing client relationships",
            D: "Knowledge of Jira"
          },
          answer: "B",
          explanation: "Michael explicitly states 'I hold a PMP certification', directly addressing that requirement."
        },
        {
          id: "RM001-Q2",
          stem: "What can be inferred about Michael Chen's application?",
          options: {
            A: "He does not meet the minimum experience requirement",
            B: "He applied after the deadline",
            C: "He exceeds the minimum years of experience required",
            D: "He currently works at Orion Consulting"
          },
          answer: "C",
          explanation: "The posting requires 7 years minimum; Michael has 9 years, so he exceeds the requirement."
        },
        {
          id: "RM001-Q3",
          stem: "What is suggested about Michael's availability?",
          options: {
            A: "He can start immediately",
            B: "He cannot start before March",
            C: "He is available after January 15th",
            D: "He requires visa sponsorship"
          },
          answer: "C",
          explanation: "Michael states he is 'available to start from January 15th'."
        },
        {
          id: "RM001-Q4",
          stem: "Which statement about the job posting is TRUE?",
          options: {
            A: "It requires candidates to be based in Taipei",
            B: "It specifies a monthly salary range",
            C: "It is posted on a job board website",
            D: "The deadline is January 15th"
          },
          answer: "B",
          explanation: "The posting clearly states 'Salary range: NT$120,000–NT$150,000 per month'."
        }
      ]
    }
  ]
};
