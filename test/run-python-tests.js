import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";

const args = ["-m", "unittest", "discover", "-s", "test", "-p", "*_test.py"];
const candidates = process.platform === "win32"
  ? [
      existsSync(".venv/Scripts/python.exe")
        ? ".venv/Scripts/python.exe"
        : null,
      "py",
      "python",
    ]
  : ["python3", "python"];

for (const command of candidates.filter(Boolean)) {
  const result = spawnSync(command, args, { stdio: "inherit" });

  if (result.error?.code === "ENOENT") continue;

  process.exit(result.status ?? 1);
}

console.error("Python 3 was not found. Create .venv or install Python 3.");
process.exit(1);
