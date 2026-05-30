#!/usr/bin/env python3
"""
THE GARDENER - Multi-Agent Code Generation & Curation Platform
A meta-application that creates specialized AI agents for code generation,
review, and ranking using a hierarchical pipeline architecture.

[...truncated; UNCHANGED LINES...]

class NoveltySiteBuilder:
    SYSTEM_PROMPT = """You are a creative coding virtuoso. Build the most NOVEL, CREATIVE, \
INNOVATIVE version possible. Push boundaries. Use unexpected patterns. Include delightful \
micro-interactions. Make code a work of art. Each iteration MORE creative than last.\nGenerate COMPLETE, runnable code."""

    def __init__(self, llm_client):
        self.llm = llm_client

    async def build_novelty_versions(self, request, winning_stack, winning_attempt):
        attempts = []
        prev_code = winning_attempt.code_artifact
        for iteration in range(1, 4):
            attempt = await self._build_iteration(request, winning_stack, iteration, prev_code, attempts)
            attempts.append(attempt)
            if attempt.success:
                prev_code = attempt.code_artifact
        # --- PATCH: guarantee fallback if all attempts fail
        if not any(a.success for a in attempts):
            fallback_attempt = NoveltyAttempt(
                attempt_id=f"novelty_fallback_{uuid.uuid4().hex[:8]}",
                iteration=0,
                winning_config=winning_stack,
                code_artifact=winning_attempt.code_artifact,
                build_log="Fallback to ranked winner's code.",
                creativity_notes="No successful novelty iterations. Fallback used.",
                build_time_seconds=0.0,
                success=True,
                timestamp=datetime.now().isoformat(),
            )
            attempts.append(fallback_attempt)
        return attempts

[...truncated; UNCHANGED LINES...]

    async def run_pipeline(self, request, build_id=None):
        build_id = build_id or f"pipeline_{uuid.uuid4().hex[:8]}"
        self.current_build_id = build_id
        self.progress[build_id] = {"status": "started", "phase": "meta_builder",
                                    "message": "The Gardener is selecting seeds...", "percent": 5}
        start_time = time.time()

        try:
            # PHASE 1: META-BUILDER
            self._update_progress(build_id, "meta_builder", "Planting 5 distinct tool combinations...", 10)
            tool_combinations = self.meta_builder.generate_tool_combinations(request.code_type.value, request.preferred_frameworks)

            # PHASE 2: BUILDER BOT (5 attempts)
            self._update_progress(build_id, "builder", "Builder Bots are constructing...", 20)
            build_tasks = [self.builder.build(request, stack, i+1) for i, stack in enumerate(tool_combinations)]
            build_attempts = await asyncio.gather(*build_tasks)

            successful = [a for a in build_attempts if a.success]
            if not successful:
                self._update_progress(build_id, "failed", "All build attempts failed", 100)
                return {"status": "failed", "error": "All builds failed"}

            # PHASE 3: REVIEWER
            self._update_progress(build_id, "reviewer", "Reviewer is analyzing code quality...", 40)
            reviews = await self.reviewer.review_all(request, build_attempts)

            # PHASE 4: RANKER
            self._update_progress(build_id, "ranker", "Ranker is scoring all builds...", 55)
            ranked_builds = await self.ranker.rank_all(build_attempts, reviews)

            winner = ranked_builds[0]
            winning_attempt = next((a for a in build_attempts if a.attempt_id == winner.attempt_id), None)
            if not winning_attempt:
                return {"status": "failed", "error": "Ranking failed"}

            # PHASE 5: NOVELTY BUILDER
            self._update_progress(build_id, "novelty", "Novelty Builder is creating magic...", 70)
            novelty_attempts = await self.novelty_builder.build_novelty_versions(request, winning_attempt.tool_stack, winning_attempt)

            successful_novelty = [a for a in novelty_attempts if a.success]
            if not successful_novelty:
                final_code = winning_attempt.code_artifact
            else:
                final_code = successful_novelty[-1].code_artifact

            # --- PATCH: sanitize novelty_attempts for JSON serialization
            novelty_attempts_clean = []
            for a in novelty_attempts:
                attempt_dict = a.dict()
                for key in ['code_artifact', 'build_log', 'creativity_notes']:
                    val = attempt_dict.get(key)
                    if isinstance(val, str):
                        attempt_dict[key] = val.encode('utf-8', errors='ignore').decode('utf-8')
                novelty_attempts_clean.append(attempt_dict)

            # PHASE 6: DOWNLOAD
            self._update_progress(build_id, "packaging", "Packaging final deliverable...", 85)
            project_name = f"{request.code_type.value}_project"
            zip_path = self.download_manager.create_package(project_name, final_code, winning_attempt.tool_stack, request)

            # PHASE 7: LEADERBOARD
            self._update_progress(build_id, "leaderboard", "Adding to leaderboard...", 95)
            total_time = time.time() - start_time

            entry = LeaderboardEntry(
                entry_id=build_id, project_name=project_name, code_type=request.code_type.value,
                score=winner.total_score, novelty_rating=winner.novelty_score,
                tool_stack=winning_attempt.tool_stack.name, build_time_seconds=total_time,
                user_rating=None, created_at=datetime.now().isoformat(),
                download_path=zip_path, model_used=winning_attempt.model_used
            )
            self.leaderboard.add_entry(entry)

            self._update_progress(build_id, "complete", "Build complete! Ready for download.", 100)

            results = {
                "status": "success", "build_id": build_id, "request": request.dict(),
                "tool_combinations": [t.dict() for t in tool_combinations],
                "build_attempts": [a.dict() for a in build_attempts],
                "reviews": [r.dict() for r in reviews],
                "ranked_builds": [r.dict() for r in ranked_builds],
                "winner": winner.dict(),
                "novelty_attempts": novelty_attempts_clean,
                "final_code": final_code, "download_path": zip_path,
                "total_time_seconds": total_time, "leaderboard_entry": entry.dict()
            }
            self.results[build_id] = results
            return results

        except Exception as e:
            self._update_progress(build_id, "failed", f"Pipeline failed: {str(e)}", 100)
            return {"status": "failed", "error": str(e)}

[...truncated; UNCHANGED LINES...]
