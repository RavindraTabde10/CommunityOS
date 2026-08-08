# Riverdale Connect - Stakeholder Input Required

This document contains important questions that need your input before proceeding with full development.

---

## 🔴 Critical Questions (Required for Version 1)

### 1. User Onboarding & Authentication
**Question:** How will initial user accounts be created?
- [ ] Bulk import from Excel/CSV (builder provides resident list)
- [ ] Self-registration with approval workflow
- [ ] Admin creates accounts manually
- [ ] Integration with existing CRM system

**Impact:** Affects authentication flow and database seeding strategy

---

### 2. Unit/Property Mapping
**Question:** Do you have a digital map or layout of the property?
- [ ] Yes, we have floor plans/unit layouts
- [ ] No, but we can provide unit numbers and structure
- [ ] We need to create this as part of the project

**Additional Info Needed:**
- Total number of units/flats: _____________
- Number of towers/blocks: _____________
- Common areas (lobbies, gardens, parking, etc.): _____________

**Impact:** Affects QR code generation and location tagging

---

### 3. Notification System
**Question:** What notification channels should be supported?
- [ ] Email only
- [ ] SMS only
- [ ] In-app notifications only
- [ ] Email + SMS
- [ ] Email + SMS + In-app (recommended)
- [ ] Push notifications (for mobile app)

**Preferences:**
- Issue creation notification: _____________
- Issue assignment notification: _____________
- Issue resolution notification: _____________
- Weekly report delivery: _____________

**Impact:** Affects service integrations and costs

---

### 4. Mobile Application Priority
**Question:** Is a native mobile app required in Version 1?
- [ ] PWA (Progressive Web App) is sufficient - works on all devices
- [ ] Native mobile app required (React Native) - separate iOS/Android apps
- [ ] Mobile app needed later (Version 2 or 3)

**Notes:**
- PWA: Works on all browsers, installable, works offline, faster to develop
- Native: Better performance, native features, app store presence, higher cost

**Impact:** Affects development timeline and budget

---

## 🟡 Important Questions (Affects Planning)

### 5. Multi-Property Support
**Question:** Will this system manage a single property or multiple properties?
- [ ] Single property (one society/project)
- [ ] Multiple properties (builder managing multiple projects)

**If multiple:**
- Number of properties initially: _____________
- Expected growth: _____________

**Impact:** Affects database design and user roles

---

### 6. Language Support
**Question:** Is multi-language support required?
- [ ] English only
- [ ] English + Hindi
- [ ] English + Regional language: _____________
- [ ] Multiple languages: _____________

**Impact:** Affects UI design and implementation complexity

---

### 7. Document Management
**Question:** What types of documents need to be stored and managed?
- [ ] Contractor agreements/contracts
- [ ] Warranty documents
- [ ] Property handover documents
- [ ] Defect rectification certificates
- [ ] Compliance certificates
- [ ] Other: _____________

**Storage requirements:**
- Expected total storage: _____________
- Document retention period: _____________

**Impact:** Affects storage costs and document management features

---

### 8. Payment Gateway (Version 3)
**Question:** For maintenance bill payments, which payment gateway should be integrated?
- [ ] Razorpay
- [ ] PayU
- [ ] Stripe
- [ ] PayTM
- [ ] Other: _____________
- [ ] To be decided later

**Impact:** Affects Version 3 planning and integration complexity

---

## 🟢 Additional Information Needed

### 9. User Roles & Permissions
**Question:** Please confirm/modify the user roles:

| Role | Access Level | Count (Approximate) |
|------|--------------|---------------------|
| Resident | View own issues, create issues | _____ |
| Contractor | View assigned issues, update status | _____ |
| Builder | Full access, analytics, reports | _____ |
| Admin | System administration | _____ |
| Security | Gate entry, material tracking | _____ |
| Facility Team | Asset management, issue assignment | _____ |

**Additional roles needed:** _____________

---

### 10. Reporting Requirements
**Question:** What should the weekly PDF report include?

Current plan:
- [ ] Issue summary (new, resolved, pending)
- [ ] Photos of completed work
- [ ] Contractor performance
- [ ] Defect trends

Additional requirements:
- [ ] Financial summary
- [ ] Attendance tracking
- [ ] Material consumption
- [ ] Other: _____________

---

### 11. Issue Categories
**Question:** Confirm or modify issue categories:

Current categories:
- Electrical
- Plumbing
- Painting
- Carpentry
- Flooring
- Civil
- Other

Additional categories needed: _____________

---

### 12. Data Retention & Compliance
**Question:** Data retention and privacy requirements:
- How long should data be retained: _____________
- Any specific compliance requirements (GDPR, etc.): _____________
- Data backup frequency: _____________
- Data export requirements: _____________

---

### 13. Integration Requirements
**Question:** Do you need integration with any existing systems?
- [ ] CRM system (specify): _____________
- [ ] Accounting software (specify): _____________
- [ ] Property management system (specify): _____________
- [ ] Other systems: _____________

---

### 14. Timeline & Budget Constraints
**Question:** Project constraints:
- Target launch date: _____________
- Budget allocated: _____________
- Number of initial users: _____________
- Expected scaling (users in 1 year): _____________

---

### 15. Hosting & Infrastructure Preferences
**Question:** Infrastructure preferences:

Current recommendation:
- Frontend: Vercel
- Backend: Vercel Serverless / Railway
- Database: Supabase
- Storage: AWS S3

Any preference changes: _____________

**Cost concerns:**
- Expected monthly budget: _____________
- Scaling concerns: _____________

---

## 📋 Action Items

### Before Development Starts
1. [ ] Review and answer all questions above
2. [ ] Provide unit/property layout or mapping data
3. [ ] Confirm user roles and permissions
4. [ ] Approve tech stack and architecture
5. [ ] Set up required accounts (Supabase, AWS, Vercel, Resend)
6. [ ] Provide branding assets (logo, colors, fonts)
7. [ ] Assign project manager/point of contact

### Design Phase
1. [ ] Review and approve wireframes
2. [ ] Provide sample data for testing
3. [ ] Define approval workflows
4. [ ] Confirm QR code placement locations

### Before Launch
1. [ ] User acceptance testing
2. [ ] Training plan for different user roles
3. [ ] Migration plan (if applicable)
4. [ ] Support and maintenance plan

---

## 📞 Next Steps

**Please:**
1. Fill out this document with your responses
2. Add any additional questions or concerns
3. Schedule a review meeting to discuss responses
4. Approve the final development plan

**Timeline:**
- Document review: _____________
- Meeting scheduled: _____________
- Development start: _____________

---

## ✉️ Contact

**For questions or clarifications, contact:**
- Project Lead: _____________
- Email: _____________
- Phone: _____________

---

**Document Version**: 1.0  
**Created**: 2026-07-22  
**Status**: Awaiting Stakeholder Input  
**Priority**: HIGH
