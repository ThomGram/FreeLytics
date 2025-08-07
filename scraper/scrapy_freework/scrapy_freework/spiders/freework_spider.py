import ast
import configparser
from itertools import product
from pathlib import Path
from urllib.parse import urlparse

import scrapy


class FreeworkSpider(scrapy.Spider):
    name = "freework"

    def generate_start_urls(self):
        """Génère les URLs de départ depuis le fichier de config."""
        try:
            config = configparser.ConfigParser()
            config_path = "../../FreeLytics.cfg"

            # Check if config file exists
            if not Path(config_path).exists():
                self.logger.error(f"Config file not found: {config_path}")
                return []

            config.read(config_path)

            # Validate config sections and keys
            if not config.has_section("freework"):
                self.logger.error("Section 'freework' not found in config file")
                return []

            required_keys = ["jobs", "locations", "contracts", "base_url"]
            for key in required_keys:
                if not config.has_option("freework", key):
                    self.logger.error(f"Key '{key}' not found in freework section")
                    return []

            # Read configuration values
            jobs = ast.literal_eval(config.get("freework", "jobs"))
            locations = ast.literal_eval(config.get("freework", "locations"))
            contracts = ast.literal_eval(config.get("freework", "contracts"))
            base_url = config.get("freework", "base_url").strip()

            # Validate base_url
            if not base_url:
                self.logger.error("base_url is empty in config file")
                return []

            # Ensure base_url has proper scheme
            parsed_url = urlparse(base_url)
            if not parsed_url.scheme:
                self.logger.error(f"base_url missing scheme (http/https): {base_url}")
                return []

            # Generate URLs
            urls = []
            for job, location, contract in product(jobs, locations, contracts):
                url = f"{base_url}{job}&locations={location}&contracts={contract}"

                # Validate each generated URL
                if self.is_valid_url(url):
                    urls.append(url)
                    self.logger.info(f"Generated URL: {url}")
                else:
                    self.logger.warning(f"Invalid URL generated: {url}")

            self.logger.info(f"Generated {len(urls)} valid URLs")
            return urls

        except Exception as e:
            self.logger.error(f"Error generating start URLs: {e}")
            return []

    def is_valid_url(self, url):
        """Validate URL format."""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme in ("http", "https") and parsed.netloc)
        except Exception:
            return False

    def start_requests(self):
        """Méthode Scrapy standard pour générer les requêtes initiales."""
        urls = self.generate_start_urls()

        if not urls:
            self.logger.error("No valid URLs generated. Check your configuration file.")
            return

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def get_total_pages_simple(self, response):
        """Version simple et efficace pour free-work.com."""
        container = response.css("div[total-items]")
        if container:
            total_items = int(container.css("::attr(total-items)").get() or 0)
            items_per_page = int(container.css("::attr(items-per-page)").get() or 16)

            if total_items > 0:
                import math

                total_pages = math.ceil(total_items / items_per_page)
                return total_pages
        return 1

    def parse(self, response):
        self.logger.info(f"Parsing search results: {response.url}")

        # Ajuste si besoin selon la structure réelle
        job_cards = response.css("div.mb-4.relative")

        for card in job_cards:
            job_url = response.urljoin(card.css("a::attr(href)").get())

            yield scrapy.Request(
                url=job_url,
                callback=self.parse_job_detail,
            )

        # # Pagination - continuer vers les pages suivantes
        # total_pages = self.get_total_pages_simple(response)
        # current_page = int(re.search(r'page=(\d+)', response.url).group(1)) if 'page=' in response.url else 1

        # self.logger.info(f"Page {current_page}/{total_pages} - {len(job_links)} job links found")

        # if current_page < total_pages:
        #     next_page = current_page + 1
        #     next_url = f"{response.url}&page={next_page}" if 'page=' not in response.url else re.sub(r'page=\d+', f'page={next_page}', response.url)
        #     yield scrapy.Request(next_url, callback=self.parse)

    def get_icon_field_mapping(self):
        """Map SVG path patterns to field types based on icon recognition."""
        return {
            # Calendar icon - Start date
            "M152 24c0-13.3-10.7-24-24-24s-24 10.7-24 24V64H64C28.7 64 0 92.7 0 "
            "128v16 48V448c0 35.3 28.7 64 64 64H384c35.3 0 64-28.7 64-64V192 144 128c0"
            "-35.3-28.7-64-64-64H344V24c0-13.3-10.7-24-24-24s-24 10.7-24 24V64H152V24z"
            "M48 192H400V448c0 8.8-7.2 16-16 16H64c-8.8 0-16-7.2-16-16V192z": "start_date",
            # Clock icon - Duration
            "M464 256A208 208 0 1 1 48 256a208 208 0 1 1 416 0zM0 256a256 256 0 1 0 "
            "512 0A256 256 0 1 0 0 256zM232 120V256c0 8 4 15.5 10.7 20l96 64c11 7.4 "
            "25.9 4.4 33.3-6.7s4.4-25.9-6.7-33.3L280 243.2V120c0-13.3-10.7-24-24-24s"
            "-24 10.7-24 24z": "duration",
            # Money/Wallet icon - Salary
            "M88 32C39.4 32 0 71.4 0 120V392c0 48.6 39.4 88 88 88H424c48.6 0 88-39.4 "
            "88-88V216c0-48.6-39.4-88-88-88H120c-13.3 0-24 10.7-24 24s10.7 24 24 24H424c"
            "22.1 0 40 17.9 40 40V392c0 22.1-17.9 40-40 40H88c-22.1 0-40-17.9-40-40V120c"
            "0-22.1 17.9-40 40-40H456c13.3 0 24-10.7 24-24s-10.7-24-24-24H88zM384 336a32 "
            "32 0 1 0 0-64 32 32 0 1 0 0 64z": "salary",
            # Briefcase icon - Experience
            "M176 56V96H336V56c0-4.4-3.6-8-8-8H184c-4.4 0-8 3.6-8 8zM128 96V56c0-30.9 "
            "25.1-56 56-56H328c30.9 0 56 25.1 56 56V96h64c35.3 0 64 28.7 64 64V416c0 "
            "35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V160c0-35.3 28.7-64 64-64h64zm"
            "232 48H152 64c-8.8 0-16 7.2-16 16V416c0 8.8 7.2 16 16 16H448c8.8 0 16-7.2 "
            "16-16V160c0-8.8-7.2-16-16-16H360z": "experience",
            # House icon - Remote work
            "M224.8 5.4c8.8-7.2 21.5-7.2 30.3 0l216 176c10.3 8.4 11.8 23.5 3.4 33.8s"
            "-23.5 11.8-33.8 3.4L416 198.4V240H368V159.3L240 55 112 159.3V360c0 4.4 3.6 "
            "8 8 8H272v48H120c-30.9 0-56-25.1-56-56V198.4L39.2 218.6c-10.3 8.4-25.4 "
            "6.8-33.8-3.4s-6.8-25.4 3.4-33.8l216-176zM288 216v45.7c-6 6.8-10.6 14.9-13.3 "
            "23.8c-3.2 1.6-6.9 2.5-10.7 2.5H216c-13.3 0-24-10.7-24-24V216c0-13.3 10.7-24 "
            "24-24h48c13.3 0 24 10.7 24 24zm64 104V464H544V320H352zm-48-16c0-17.7 14.3-32 "
            "32-32H560c17.7 0 32 14.3 32 32V464h36c6.6 0 12 5.4 12 12c0 19.9-16.1 36-36 "
            "36H592 544 352 304 292c-19.9 0-36-16.1-36-36c0-6.6 5.4-12 12-12h36V304z": "remote_work",
            # Location icon - Location
            "M320.7 249.2c-10.5 24.8-25.4 52.2-42.5 79.9C249.8 375.3 216.8 420 192 "
            "451.7c-24.8-31.8-57.8-76.4-86.2-122.6c-17.1-27.7-32-55.1-42.5-79.9C52.5 "
            "223.6 48 204.4 48 192c0-79.5 64.5-144 144-144s144 64.5 144 144c0 12.4-4.5 "
            "31.6-15.3 57.2zm-105 250C267 435 384 279.4 384 192C384 86 298 0 192 0S0 86 "
            "0 192c0 87.4 117 243 168.3 307.2c12.3 15.3 35.1 15.3 47.4 0z": "location",
        }

    def _process_salary_field(self, value):
        """Process salary field and split salary/daily rate."""
        result = {"salary": "", "daily_rate": ""}

        if "€⁄an" in value and "€⁄j" in value:
            parts = value.split(", ")
            if len(parts) == 2:
                result["salary"] = parts[0].strip()
                result["daily_rate"] = parts[1].strip()
            else:
                result["salary"] = value
        elif "€⁄j" in value:
            result["daily_rate"] = value
        elif "€⁄an" in value:
            result["salary"] = value
        else:
            result["salary"] = value

        return result

    def _clean_text(self, text):
        """Clean and normalize text."""
        if text is None:
            return ""
        if isinstance(text, str):
            # Replace non-breaking space with regular space
            cleaned = text.replace("\xa0", " ")
            return cleaned.strip()
        return str(text).strip()

    def _process_contract_types(self, contract_list):
        """Process contract types list."""
        return [text.strip() for text in contract_list if text.strip()]

    def _process_skills(self, skills_list):
        """Process skills list."""
        return [skill.strip() for skill in skills_list if skill.strip()]

    def _process_description(self, paragraphs):
        """Process description paragraphs."""
        return [para.strip() for para in paragraphs if para.strip()]

    def _match_icon_to_field(self, svg_path, mapping):
        """Match SVG icon path to field name."""
        for path_start, field_name in mapping.items():
            if svg_path.startswith(path_start):
                return field_name
        return None

    def parse_job_detail(self, response):
        """Parse une page individuelle d'emploi et extrait les détails."""
        self.logger.info(f"Parsing job detail: {response.url}")

        # Récupérer le titre
        job_title = response.xpath("//h1/text()[normalize-space()]").get()

        # Extraire les données de la sidebar avec mapping par icône
        sidebar_data = {}
        icon_mapping = self.get_icon_field_mapping()

        # Trouver tous les éléments de la sidebar
        sidebar_rows = response.css("div.flex.flex-col.gap-2")

        row = sidebar_rows[1]
        # Extraire le path de l'icône SVG
        svg_paths = row.css("svg path::attr(d)").getall()
        # Extraire la valeur
        values = row.css("span.w-full.text-sm.line-clamp-2::text").getall()

        if svg_paths and values:
            # Traiter chaque path SVG individuellement avec chaque valeur
            for svg_path, value in zip(svg_paths, values):
                if svg_path and value:
                    value = value.strip()

                    # Use extracted method for icon matching
                    field_type = self._match_icon_to_field(svg_path, icon_mapping)

                    if field_type:
                        if field_type == "salary":
                            # Use extracted method for salary processing
                            salary_data = self._process_salary_field(value)
                            sidebar_data.update(salary_data)
                        else:
                            sidebar_data[field_type] = self._clean_text(value)

        # Extraire les autres détails
        try:
            company_name = response.css("p.font-semibold.text-sm::text").get()
            company_name = company_name.strip() if company_name else ""

            contract_types = self._process_contract_types(
                response.css("div.tags span.tag div.truncate::text").getall()
            )
            description = response.css("div.html-renderer.prose-content").getall()
            # description = ' '.join(description).strip() if description else ''

            company_description = response.css(
                "div.flex.items-center.mr-6.mb-4 span::text"
            ).getall()
            # company_description = ' '.join(company_description).strip() if company_description else ''

            # Date de publication
            publication_date = (
                response.xpath(
                    "/html/body/div/div/div/div/div[1]/div/div/div/div[1]/div[2]/div[1]/div[1]/span/text()"
                ).get()
                or ""
            )

            # Technologies/compétences
            skills = self._process_skills(response.css("a.tag div.truncate::text").getall())

            yield {
                "job_title": job_title.strip() if job_title else "",
                "job_url": response.url,
                "company_name": company_name,
                "contract_types": contract_types,
                "description": description,
                "company_description": company_description,
                "publication_date": publication_date.strip() if publication_date else "",
                "skills": skills,
                "start_date": sidebar_data.get("start_date", ""),
                "duration": sidebar_data.get("duration", ""),
                "salary": sidebar_data.get("salary", ""),
                "daily_rate": sidebar_data.get("daily_rate", ""),
                "experience": sidebar_data.get("experience", ""),
                "remote_work": sidebar_data.get("remote_work", ""),
                "location": sidebar_data.get("location", ""),
            }

        except Exception as e:
            self.logger.error(f"Error parsing job detail {response.url}: {e}")
            # En cas d'erreur, yield au moins les informations de base
            yield {"ad_title": job_title, "job_url": response.url, "error": f"Parsing error: {e}"}
