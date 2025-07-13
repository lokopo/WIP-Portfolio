export interface JobApplication {
  id: string;
  company: string;
  position: string;
  jobDescription: string;
  applicationDate: Date;
  status: ApplicationStatus;
  salary?: string;
  location?: string;
  contactPerson?: string;
  contactEmail?: string;
  contactPhone?: string;
  jobUrl?: string;
  notes?: string;
  resume: Resume;
  coverLetter?: CoverLetter;
  documents: Document[];
  followUpDate?: Date;
  interviewDate?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export enum ApplicationStatus {
  APPLIED = 'Applied',
  UNDER_REVIEW = 'Under Review',
  INTERVIEW_SCHEDULED = 'Interview Scheduled',
  INTERVIEWED = 'Interviewed',
  OFFER_RECEIVED = 'Offer Received',
  OFFER_ACCEPTED = 'Offer Accepted',
  REJECTED = 'Rejected',
  WITHDRAWN = 'Withdrawn',
  NO_RESPONSE = 'No Response'
}

export interface Resume {
  id: string;
  name: string;
  content: string;
  fileName: string;
  fileSize?: number;
  createdAt: Date;
}

export interface CoverLetter {
  id: string;
  name: string;
  content: string;
  fileName: string;
  fileSize?: number;
  createdAt: Date;
}

export interface Document {
  id: string;
  name: string;
  type: DocumentType;
  fileName: string;
  fileSize?: number;
  description?: string;
  createdAt: Date;
}

export enum DocumentType {
  RESUME = 'Resume',
  COVER_LETTER = 'Cover Letter',
  PORTFOLIO = 'Portfolio',
  CERTIFICATE = 'Certificate',
  REFERENCE = 'Reference',
  OTHER = 'Other'
}

export interface DashboardStats {
  totalApplications: number;
  activeApplications: number;
  interviewsScheduled: number;
  offersReceived: number;
  applicationsThisMonth: number;
  averageResponseTime: number;
}