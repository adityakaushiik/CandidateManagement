import asyncio
import os
import re
import tempfile
from pathlib import Path

import spacy


class ResumeParser:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    async def _save_upload_to_temp(self, upload_file):
        """Save uploaded file to temporary location and return the path"""
        # Get file extension from filename
        file_extension = os.path.splitext(upload_file.filename)[1]

        # Create temporary file
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        try:
            # Read content from upload
            content = await upload_file.read()
            # Write to temp file
            tmp_file.write(content)
            tmp_file.close()
            return tmp_file.name
        except Exception as e:
            # Clean up on error
            tmp_file.close()
            if os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)
            raise e

    async def _extract_text(self, file_path):
        """Extract text from the file based on extension"""
        file_extension = Path(file_path).suffix.lower()

        if file_extension == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif file_extension == ".pdf":
            try:
                from pdfminer.high_level import extract_text as pdf_extract_text

                return pdf_extract_text(file_path)
            except Exception as e:
                print(f"Error extracting PDF: {e}")
                return ""
        elif file_extension in [".docx", ".doc"]:
            try:
                import docx2txt

                return docx2txt.process(file_path)
            except Exception as e:
                print(f"Error extracting DOCX: {e}")
                return ""
        else:
            return ""

    async def _count_pages(self, file_path):
        """Count number of pages in PDF"""
        file_extension = Path(file_path).suffix.lower()

        if file_extension == ".pdf":
            try:
                import PyPDF2

                with open(file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    return len(pdf_reader.pages)
            except:
                # Alternative method using pdfminer
                try:
                    from pdfminer.pdfpage import PDFPage

                    with open(file_path, "rb") as f:
                        return len(list(PDFPage.get_pages(f)))
                except:
                    return None
        return None

    async def _extract_name(self, doc, text):
        """Extract name using spaCy NER"""
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()

        # Fallback: try to get name from first line
        lines = text.strip().split("\n")
        if lines:
            first_line = lines[0].strip()
            # Check if first line looks like a name (2-4 words, capitalized)
            words = first_line.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                return first_line
        return None

    async def _extract_email(self, text):
        """Extract email using regex"""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None

    async def _extract_phone(self, text):
        """Extract phone number using regex and format it"""
        # Pattern for various phone formats
        phone_patterns = [
            r"\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            r"\b\d{10}\b",  # 10 digit number
            r"\+?\d{10,}",
        ]

        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                phone = phones[0].strip()
                # Format phone number: add + prefix if not present and looks international
                if len(re.sub(r"\D", "", phone)) > 10 and not phone.startswith("+"):
                    phone = "+" + phone
                return phone
        return None

    async def _extract_links(self, text):
        """Extract LinkedIn, GitHub, Portfolio, and other professional links"""
        links = {"linkedin": None, "github": None, "portfolio": None, "other": []}

        # LinkedIn pattern
        linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+"
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            links["linkedin"] = linkedin_matches[0]

        # GitHub pattern
        github_pattern = r"(?:https?://)?(?:www\.)?github\.com/[\w-]+"
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        if github_matches:
            links["github"] = github_matches[0]

        # Portfolio/website pattern
        portfolio_pattern = r"https?://[\w\.-]+\.[\w]{2,}(?:/[\w\.-]*)*"
        all_urls = re.findall(portfolio_pattern, text, re.IGNORECASE)

        for url in all_urls:
            url_lower = url.lower()
            if "linkedin" not in url_lower and "github" not in url_lower:
                if not links["portfolio"]:
                    links["portfolio"] = url
                else:
                    links["other"].append(url)

        # Remove empty 'other' list if no additional links
        if not links["other"]:
            del links["other"]

        return links if any(v for k, v in links.items() if k != "other") else None

    async def _extract_location(self, doc):
        """Extract location/address information"""
        locations = []

        # Extract GPE (Geopolitical Entity) and LOC (Location)
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                locations.append(ent.text)

        # Return the most common location or first one found
        if locations:
            # Remove duplicates and common non-location terms
            unique_locs = []
            seen = set()
            for loc in locations:
                loc_lower = loc.lower()
                if loc_lower not in seen and loc_lower not in ["remote", "online"]:
                    seen.add(loc_lower)
                    unique_locs.append(loc)

            return unique_locs[0] if unique_locs else None
        return None

    async def _extract_skills(self, doc, text):
        """Extract skills from predefined list"""
        # Common technical skills
        skill_keywords = [
            "python",
            "java",
            "javascript",
            "c++",
            "c#",
            "ruby",
            "php",
            "swift",
            "kotlin",
            "react",
            "angular",
            "vue",
            "node",
            "django",
            "flask",
            "fastapi",
            "spring",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "git",
            "jenkins",
            "ci/cd",
            "sql",
            "mysql",
            "postgresql",
            "mongodb",
            "redis",
            "elasticsearch",
            "machine learning",
            "deep learning",
            "nlp",
            "computer vision",
            "ai",
            "tensorflow",
            "pytorch",
            "keras",
            "scikit-learn",
            "pandas",
            "numpy",
            "html",
            "css",
            "typescript",
            "sass",
            "webpack",
            "rest api",
            "graphql",
            "spacy",
            "nltk",
            "linux",
            "bash",
            "shell",
            "agile",
            "scrum",
        ]

        text_lower = text.lower()
        found_skills = []

        for skill in skill_keywords:
            # Use word boundaries to avoid partial matches
            if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
                # Capitalize properly
                if skill in ["ai", "nlp", "ci/cd", "html", "css", "sql", "aws", "gcp"]:
                    found_skills.append(skill.upper())
                else:
                    found_skills.append(skill.title())

        return sorted(list(set(found_skills))) if found_skills else None

    async def _extract_experience(self, doc, text):
        """Extract years of experience - updated to handle yrs, yr, years"""
        # Patterns for various experience formats
        exp_patterns = [
            r"(\d+\.?\d*)\+?\s*years?",  # "5 years", "5+ years", "5.5 years"
            r"(\d+\.?\d*)\+?\s*yrs?",  # "5 yrs", "5+ yrs", "5 yr"
        ]

        matches = []
        text_lower = text.lower()

        for pattern in exp_patterns:
            found = re.findall(pattern, text_lower)
            matches.extend(found)

        if matches:
            years = [float(m) for m in matches]
            max_years = max(years)
            # Return as integer if it's a whole number
            return int(max_years) if max_years.is_integer() else max_years
        return None

    async def _extract_education(self, doc, text):
        """Extract degree and college information"""
        degree = None
        college = None

        # Common degree patterns
        degree_patterns = [
            r"\b(B\.?Tech|Bachelor of Technology|B\.?E\.?|Bachelor of Engineering)\b",
            r"\b(M\.?Tech|Master of Technology|M\.?E\.?|Master of Engineering)\b",
            r"\b(B\.?S\.?|Bachelor of Science|B\.?Sc\.?)\b",
            r"\b(M\.?S\.?|Master of Science|M\.?Sc\.?)\b",
            r"\b(MBA|Master of Business Administration)\b",
            r"\b(Ph\.?D\.?|Doctor of Philosophy)\b",
            r"\b(BCA|Bachelor of Computer Applications)\b",
            r"\b(MCA|Master of Computer Applications)\b",
        ]

        for pattern in degree_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                degree = match.group(1)
                break

        # Extract college/university names
        college_keywords = ["university", "college", "institute", "school"]
        for ent in doc.ents:
            if ent.label_ == "ORG":
                ent_lower = ent.text.lower()
                if any(keyword in ent_lower for keyword in college_keywords):
                    college = ent.text.strip()
                    break

        return degree, college

    async def _extract_designation(self, text):
        """Extract current or most recent job designation/title"""
        # Common job title patterns
        title_patterns = [
            r"(?:Current|Present)[\s:]+(.+?)(?:\n|at)",
            r"(?:Position|Role|Title)[\s:]+(.+?)(?:\n|$)",
            r"\b(Software Engineer|Senior Software Engineer|Lead Engineer|Tech Lead|Engineering Manager)\b",
            r"\b(Data Scientist|Data Analyst|Machine Learning Engineer|AI Engineer)\b",
            r"\b(Full Stack Developer|Frontend Developer|Backend Developer|Web Developer)\b",
            r"\b(DevOps Engineer|Cloud Engineer|Solutions Architect)\b",
            r"\b(Product Manager|Project Manager|Scrum Master)\b",
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                designation = match.group(1).strip()
                # Clean up the designation
                designation = re.sub(r"\s+", " ", designation)
                if len(designation) > 5 and len(designation) < 100:
                    return designation

        return None

    async def _extract_companies(self, doc, text):
        """Extract company names using spaCy NER with improved filtering"""
        # Common words that are NOT company names
        exclude_terms = {
            "angular",
            "typescript",
            "sql",
            "javascript",
            "python",
            "java",
            "websockets",
            "data structures",
            "ai/ml",
            "render",
            "google oauth",
            "msc",
            "sqs",
            "aws",
            "gcp",
            "azure",
            "docker",
            "kubernetes",
            "uttar pradesh",
            "delhi",
            "mumbai",
            "bangalore",
            "hyderabad",
            "bachelor of technology",
            "master of technology",
            "b.tech",
            "m.tech",
            "rest api",
            "graphql",
            "nodejs",
            "reactjs",
        }

        companies = []
        seen_normalized = set()  # Track normalized company names to avoid duplicates

        for ent in doc.ents:
            if ent.label_ == "ORG":
                ent_text = ent.text.strip()
                ent_lower = ent_text.lower()

                # Filter out skills, locations, degrees
                if ent_lower in exclude_terms:
                    continue

                # Filter out single words that are likely not companies
                if len(ent_text.split()) == 1 and len(ent_text) < 4:
                    continue

                # Filter out entries with newlines (likely parsing errors)
                if "\n" in ent_text:
                    continue

                # Check if it contains company indicators
                is_likely_company = (
                    "pvt" in ent_lower
                    or "ltd" in ent_lower
                    or "inc" in ent_lower
                    or "corp" in ent_lower
                    or "llc" in ent_lower
                    or "limited" in ent_lower
                    or "company" in ent_lower
                    or len(ent_text.split()) >= 2  # Multi-word organizations
                )

                # Filter out if it looks like an educational institution
                is_education = any(
                    keyword in ent_lower
                    for keyword in ["university", "college", "institute", "school"]
                )

                if is_likely_company and not is_education:
                    # Normalize company name for duplicate detection
                    # Remove common suffixes for comparison
                    normalized = re.sub(
                        r"\s*(pvt\.?|ltd\.?|inc\.?|llc|limited|corp\.?)\s*",
                        "",
                        ent_lower,
                        flags=re.IGNORECASE,
                    ).strip()
                    normalized = re.sub(
                        r"[^\w\s]", "", normalized
                    )  # Remove punctuation

                    if normalized not in seen_normalized:
                        seen_normalized.add(normalized)
                        companies.append(ent_text)

        return companies if companies else None

    async def _extract_certifications(self, text):
        """Extract certifications from resume"""
        cert_patterns = [
            r"(?:certified|certificate|certification)[\s:]+([\w\s\-\(\)\.]+?)(?:\n|$|\|)",
            r"(?:AWS|Azure|Google Cloud|GCP|Oracle|Microsoft|Cisco|CompTIA|PMP)\s+(?:Certified\s+)?[\w\s-]+(?:Engineer|Developer|Architect|Associate|Professional)",
        ]

        certifications = []
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)

        # Clean up and deduplicate
        cleaned_certs = []
        for cert in certifications:
            cert = cert.strip()
            if len(cert) > 5 and cert not in cleaned_certs:
                cleaned_certs.append(cert)

        return cleaned_certs[:5] if cleaned_certs else None  # Limit to 5 certifications

    async def _extract_languages(self, text):
        """Extract programming and spoken languages"""
        # Programming languages
        prog_langs = [
            "python",
            "java",
            "javascript",
            "typescript",
            "c++",
            "c#",
            "ruby",
            "php",
            "swift",
            "kotlin",
            "go",
            "rust",
            "scala",
            "r",
            "matlab",
        ]

        # Spoken languages
        spoken_langs = [
            "english",
            "hindi",
            "spanish",
            "french",
            "german",
            "chinese",
            "japanese",
            "korean",
            "arabic",
            "portuguese",
            "russian",
        ]

        text_lower = text.lower()

        found_spoken = []
        for lang in spoken_langs:
            if re.search(r"\b" + lang + r"\b", text_lower):
                found_spoken.append(lang.title())

        return found_spoken if found_spoken else None

    async def _extract_summary(self, text):
        """Extract professional summary or objective"""
        summary_patterns = [
            r"(?:professional\s+)?summary[\s:]+(.{50,500}?)(?:\n\n|\n[A-Z])",
            r"(?:career\s+)?objective[\s:]+(.{50,500}?)(?:\n\n|\n[A-Z])",
            r"(?:about\s+me|profile)[\s:]+(.{50,500}?)(?:\n\n|\n[A-Z])",
        ]

        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                # Clean up the summary
                summary = re.sub(r"\s+", " ", summary)  # Normalize whitespace
                return summary[:500]  # Limit length

        return None

    async def _extract_projects(self, text):
        """Extract project information"""
        # Look for project section
        project_pattern = (
            r"(?:projects?|personal\s+projects?)[\s:]+(.{100,1000}?)(?:\n\n[A-Z]|$)"
        )
        match = re.search(project_pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            projects_text = match.group(1)
            # Split by bullet points or newlines
            project_list = re.split(r"\n\s*[•\-*]|\n\n", projects_text)

            projects = []
            for proj in project_list[:5]:  # Limit to 5 projects
                proj = proj.strip()
                if len(proj) > 20:
                    projects.append(proj[:200])  # Limit each project description

            return projects if projects else None

        return None

    async def parse(self, file_path):
        """Parse the resume and extract all information using asyncio for parallel processing

        Args:
            file_path: Can be either a string file path or an UploadFile object from FastAPI
        """
        temp_file_path = None
        try:
            # Check if it's an UploadFile object (has 'filename' attribute)
            if hasattr(file_path, "filename"):
                # It's an UploadFile, save it temporarily
                temp_file_path = await self._save_upload_to_temp(file_path)
                actual_file_path = temp_file_path
            else:
                # It's a string file path
                actual_file_path = file_path

            # Extract text from file
            text = await self._extract_text(actual_file_path)

            if not text:
                return self._empty_result()

            # Process text with spaCy (this is CPU-bound but needed for doc object)
            doc = self.nlp(text)

            # Run all extraction methods concurrently
            results = await asyncio.gather(
                self._extract_name(doc, text),
                self._extract_email(text),
                self._extract_phone(text),
                self._extract_skills(doc, text),
                self._extract_education(doc, text),
                self._extract_companies(doc, text),
                self._extract_experience(doc, text),
                self._extract_designation(text),
                self._extract_links(text),
                self._extract_location(doc),
                self._count_pages(actual_file_path),
                self._extract_certifications(text),
                self._extract_languages(text),
                self._extract_summary(text),
                self._extract_projects(text),
            )

            # Unpack results
            (
                name,
                email,
                phone,
                skills,
                education_result,
                companies,
                experience,
                designation,
                links,
                location,
                pages,
                certifications,
                languages,
                summary,
                projects,
            ) = results

            # Unpack education tuple
            degree, college = education_result

            result = {
                "name": name,
                "email": email,
                "mobile_number": phone,
                "location": location,
                "skills": skills,
                "college_name": college,
                "degree": degree,
                "designation": designation,
                "experience": companies,
                "company_names": companies,
                "no_of_pages": pages,
                "total_experience": f"{experience} years" if experience else None,
            }

            # Add optional fields only if they have values
            if links:
                result["links"] = links
            if certifications:
                result["certifications"] = certifications
            if languages:
                result["languages"] = languages
            if summary:
                result["summary"] = summary
            if projects:
                result["projects"] = projects

            return result

        except Exception as e:
            print(f"Error parsing resume: {e}")
            import traceback

            traceback.print_exc()
            return self._empty_result()
        finally:
            # Clean up temporary file if it was created
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def _empty_result(self):
        """Return empty result structure"""
        return {
            "name": None,
            "email": None,
            "mobile_number": None,
            "location": None,
            "skills": None,
            "college_name": None,
            "degree": None,
            "designation": None,
            "experience": None,
            "company_names": None,
            "no_of_pages": None,
            "total_experience": None,
        }


resume_parser = None


def get_resume_parser():
    # Singleton pattern to reuse the ResumeParser instance
    global resume_parser
    if resume_parser is None:
        resume_parser = ResumeParser()
    return resume_parser
