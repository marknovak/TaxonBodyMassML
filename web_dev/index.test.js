import * as module from "./index.js";
import { describe, it, expect, vi, beforeEach } from "vitest";

function $(id) {
  return document.getElementById(id);
}

beforeEach(() => {
  document.body.innerHTML = `
    <div id="input-box">
      <input type="text" id="inputBar" value="" />
      <button id="go-button">Go!</button>
    </div>
    <div id="csv-check" class="hidden"></div>
    <div id="output-box" class="hidden">
      <div id="massOutput"></div>
      <button id="learn-more-arrow" class="hidden"></button>
    </div>
  `;

  module.initializeDOM();
  vi.restoreAllMocks();
  vi.spyOn(module, "myLookupMicroservice").mockResolvedValue({});
});

describe("handleGoClick()", () => {
  it("should update DOM and show success message for a known species", async () => {
    $("inputBar").value = "Homo sapiens";
    module.myLookupMicroservice.mockResolvedValue({
      status: "success",
      message: "Homo sapiens mass = 12000 g",
    });

    await module.handleGoClick();

    expect(module.myLookupMicroservice).toHaveBeenCalledWith("Homo sapiens");
    expect($("massOutput").textContent).toBe("success: Homo sapiens mass = 12000 g");
    expect($("inputBar").value).toBe("");
  });

  it("should show error message for an unknown species", async () => {
    $("inputBar").value = "Tyrannosaurus rex";
    module.myLookupMicroservice.mockResolvedValue({
      status: "error",
      error: "Species not found",
    });

    await module.handleGoClick();

    expect(module.myLookupMicroservice).toHaveBeenCalledWith("Tyrannosaurus rex");
    expect($("massOutput").textContent).toBe("not success: Species not found");
  });

  it('should display "no input" if input bar is empty', async () => {
    $("inputBar").value = "";
    await module.handleGoClick();
    expect(module.myLookupMicroservice).not.toHaveBeenCalled();
    expect($("massOutput").textContent).toBe("no input");
  });
});

describe("Input Type Toggling", () => {
  it("should make csvCheck visible when list is clicked", () => {
    const el = $("csv-check");
    el.classList.add("hidden");
    module.handleListClick();
    expect(el.classList.contains("hidden")).toBe(false);
  });

  it("should keep csvCheck visible if already visible", () => {
    const el = $("csv-check");
    el.classList.remove("hidden");
    module.handleListClick();
    expect(el.classList.contains("hidden")).toBe(false);
  });

  it("should keep csvCheck hidden when single clicked while hidden", () => {
    const el = $("csv-check");
    el.classList.add("hidden");
    module.handleSingleClick();
    expect(el.classList.contains("hidden")).toBe(true);
  });

  it("should hide csvCheck when single clicked while visible", () => {
    const el = $("csv-check");
    el.classList.remove("hidden");
    module.handleSingleClick();
    expect(el.classList.contains("hidden")).toBe(true);
  });
});
