# Docstring Standards Reference

Language-specific documentation format standards for the code-documenter skill.

## Python

### Google Style (Recommended)

```python
def calculate_discount(price: float, percentage: float) -> float:
    """Calculate the discounted price.

    One-line summary followed by blank line, then detailed description
    if needed.

    Args:
        price: Original price in dollars.
        percentage: Discount percentage between 0 and 100.

    Returns:
        The final price after applying the discount.

    Raises:
        ValueError: If percentage is not between 0 and 100.

    Example:
        >>> calculate_discount(100.0, 20)
        80.0
    """
```

**Section Order**: Summary, Description, Args, Returns, Raises, Example

### NumPy Style

```python
def calculate_discount(price, percentage):
    """
    Calculate the discounted price.

    Longer description of the function behavior.

    Parameters
    ----------
    price : float
        Original price in dollars.
    percentage : float
        Discount percentage between 0 and 100.

    Returns
    -------
    float
        The final price after applying the discount.

    Raises
    ------
    ValueError
        If percentage is not between 0 and 100.

    Examples
    --------
    >>> calculate_discount(100.0, 20)
    80.0
    """
```

**Best For**: Scientific/data projects (NumPy, Pandas, SciPy ecosystem)

### Sphinx (reStructuredText)

```python
def calculate_discount(price, percentage):
    """Calculate the discounted price.

    :param price: Original price in dollars.
    :type price: float
    :param percentage: Discount percentage between 0 and 100.
    :type percentage: float
    :returns: The final price after applying the discount.
    :rtype: float
    :raises ValueError: If percentage is not between 0 and 100.
    """
```

**Best For**: Projects using Sphinx documentation generator

---

## TypeScript/JavaScript

### JSDoc

```typescript
/**
 * Calculate the discounted price.
 *
 * @param price - Original price in dollars
 * @param percentage - Discount percentage (0-100)
 * @returns The final price after discount
 * @throws {RangeError} If percentage is not between 0 and 100
 *
 * @example
 * calculateDiscount(100, 20); // Returns 80
 */
function calculateDiscount(price: number, percentage: number): number {
```

**Key Tags**: @param, @returns, @throws, @example, @deprecated, @see

### TSDoc

```typescript
/**
 * Calculate the discounted price.
 *
 * @remarks
 * This function validates the percentage range before calculation.
 *
 * @param price - Original price in dollars
 * @param percentage - Discount percentage (0-100)
 * @returns The final price after discount
 *
 * @example
 * Here's an example:
 * ```typescript
 * const result = calculateDiscount(100, 20);
 * console.log(result); // 80
 * ```
 */
```

**TSDoc-specific Tags**: @remarks, @packageDocumentation, @defaultValue

---

## Java (Javadoc)

```java
/**
 * Calculate the discounted price.
 *
 * <p>This method validates that the percentage is within
 * the valid range before performing the calculation.</p>
 *
 * @param price      the original price in dollars
 * @param percentage the discount percentage (0-100)
 * @return the final price after applying the discount
 * @throws IllegalArgumentException if percentage is not between 0 and 100
 * @since 1.0
 * @see PriceCalculator#applyTax
 */
public double calculateDiscount(double price, double percentage) {
```

**Tag Order**: @param (declaration order), @return, @throws (alpha), @see, @since, @deprecated

---

## Go (godoc)

```go
// CalculateDiscount returns the price after applying a percentage discount.
// The percentage must be between 0 and 100.
//
// Example:
//
//	result := CalculateDiscount(100.0, 20)
//	fmt.Println(result) // Output: 80.0
func CalculateDiscount(price, percentage float64) (float64, error) {
```

**Convention**:
- Start with function name
- Write like prose, not markup
- Indent examples with tab

---

## Rust (rustdoc)

```rust
/// Calculate the discounted price.
///
/// Returns the price after applying the given percentage discount.
/// The percentage must be between 0 and 100.
///
/// # Arguments
///
/// * `price` - The original price in dollars
/// * `percentage` - The discount percentage (0-100)
///
/// # Returns
///
/// The final price after applying the discount.
///
/// # Errors
///
/// Returns an error if percentage is not between 0 and 100.
///
/// # Examples
///
/// ```
/// let result = calculate_discount(100.0, 20.0)?;
/// assert_eq!(result, 80.0);
/// ```
pub fn calculate_discount(price: f64, percentage: f64) -> Result<f64, DiscountError> {
```

**Sections**: Arguments, Returns, Errors, Panics, Examples, Safety (for unsafe)

---

## Quick Reference Table

| Language | Style | Summary Location | Param Format | Return Format |
|----------|-------|------------------|--------------|---------------|
| Python | Google | First line | `name: description` | `Returns:` section |
| Python | NumPy | First line | `name : type` | `Returns` header |
| Python | Sphinx | First line | `:param name:` | `:returns:` |
| JS/TS | JSDoc | First line | `@param name -` | `@returns` |
| Java | Javadoc | First line | `@param name` | `@return` |
| Go | godoc | First line | In prose | In prose |
| Rust | rustdoc | First line | `# Arguments` | `# Returns` |
