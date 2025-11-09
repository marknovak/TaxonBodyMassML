import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as module from './index.js';
const { handleGoClick, handleListClick, handleSingleClick, myFakeMicroservice } = module;

beforeEach(() => {
  document.body.innerHTML = `
      <div id="inputBox">
          <input type="text" id="inputBar" value=""/>
          <button id="goButton">Go!</button>
      </div>
      <div id="singleButton"></div>
      <div id="listButton"></div>
      <div id="singleOrList"></div>
      <div id="csvCheck" class="hidden"></div>
      <div id="outputBox" class="hidden">
          <div id="massOutput"></div>
          <div id="confidenceOutput"></div>
          <button id="learnMoreArrow" class="hidden"></button>
      </div>
      <div id="explanationModal"></div>
      <div id="goBackButton"></div>
      <div id="introBox"></div>
      <div id="closeIntro"></div>
  `;

  // --- Call the real DOM initializer from your module ---
  if (typeof module.initializeDOM === 'function') {
    module.initializeDOM();
  }

    inputBar = document.getElementById('inputBar');
  massOutput = document.getElementById('massOutput');
  csvCheck = document.getElementById('csvCheck');

  // Spy on the fake microservice (mocked behavior)
  vi.spyOn(module, 'myFakeMicroservice');
});


describe('handleGoClick()', () => {
  it('should update DOM and show success message for a known species', async () => {
    inputBar.value = 'Homo sapiens';
    module.myFakeMicroservice.mockResolvedValue({ status: 'success', message: 'Homo sapiens' });

    await handleGoClick();

    expect(module.myFakeMicroservice).toHaveBeenCalledWith('Homo sapiens');
    expect(massOutput.textContent).toBe('success: Homo sapiens');
    expect(inputBar.value).toBe('');
    expect(outputBox.classList.contains('hidden')).toBe(false);
    expect(learnMoreArrow.classList.contains('hidden')).toBe(false);
    expect(goButton.textContent).toBe('Go Again!');
  });

  it('should show error message for an unknown species', async () => {
    inputBar.value = 'Tyrannosaurus rex';
    module.myFakeMicroservice.mockResolvedValue({ status: 'error', error: 'not found' });

    await handleGoClick();

    expect(massOutput.textContent).toBe('not success: not found');
    expect(outputBox.classList.contains('hidden')).toBe(false);
  });

  it('should display "no input" if input bar is empty', async () => {
    inputBar.value = '';
    await handleGoClick();
    expect(massOutput.textContent).toBe('no input');
    expect(module.myFakeMicroservice).not.toHaveBeenCalled();
  });

  it('should handle a microservice network error', async () => {
    inputBar.value = 'Test error';
    module.myFakeMicroservice.mockRejectedValue(new Error('Network failure'));

    await handleGoClick();

    expect(massOutput.textContent).toBe('Error');
  });
});

describe('Input Type Toggling', () => {
  beforeEach(() => {
    csvCheck.classList.add('hidden');
  });

  describe('handleListClick()', () => {
    it('should make csvCheck visible when it starts hidden', () => {
      handleListClick();
      expect(csvCheck.classList.contains('hidden')).toBe(false);
    });

    it('should keep csvCheck visible if it is already visible', () => {
      csvCheck.classList.remove('hidden');
      handleListClick();
      expect(csvCheck.classList.contains('hidden')).toBe(false);
    });
  });

  describe('handleSingleClick()', () => {
    it('should keep csvCheck hidden when it starts hidden', () => {
      handleSingleClick();
      expect(csvCheck.classList.contains('hidden')).toBe(true);
    });

    it('should hide csvCheck when it starts visible', () => {
      csvCheck.classList.remove('hidden');
      handleSingleClick();
      expect(csvCheck.classList.contains('hidden')).toBe(true);
    });
  });
});
