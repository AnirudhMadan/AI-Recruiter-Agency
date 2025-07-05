with tab2:
                            st.subheader("Matched Positions")
                            if not result["job_matches"]["matched_jobs"]:
                                st.warning("No suitable positions found.")
                            seen_titles = set()
                            for job in result["job_matches"]["matched_jobs"]:
                                if job["title"] in seen_titles:
                                    continue
                                seen_titles.add(job["title"])
                                with st.container():
                                    col1, col2, col3 = st.columns([2, 1, 1])
                                    col1.write(f"**{job['title']}**")
                                    col2.write(f"Match: {job.get('match_score', 'N/A')}")
                                    col3.write(f"📍 {job.get('location', 'N/A')}")
                                st.divider()