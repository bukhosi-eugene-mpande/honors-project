# Mohlers Dataset Rubric

### **Section 1: Fundamentals**  
#### **1.1: Role of a prototype program**  
- **5 points**: "Simulate the behavior of portions of the desired software product."  
- **Partial (3-4)**: Mentions "high-risk problem resolution," "feasibility testing," or "demonstrating functionality to stakeholders."  

#### **1.2: Testing stage influences**  
- **5 points**: Explicitly states "coding stage (phase 5)" and "solution refinement stage (phase 7)."  
- **Partial (3)**: Refers to design flaws, production delays, or code rewrites due to testing.  

#### **1.3: OOP advantages**  
- **5 points**: Lists "abstraction" and "reusability."  
- **Partial (4-4.5)**: Mentions modularity, inheritance, polymorphism, or security.  

#### **1.4: C++ program execution start**  
- **5 points**: Correctly identifies "main function" (e.g., `int main()`).  
- **0 points**: Vague answers like "the beginning."  

#### **1.5: Variable definition**  
- **5 points**: "A location in memory that stores a value."  
- **Partial (1-2)**: Incorrectly defines as "integer or string."  

#### **1.6: Variable declaration in C++**  
- **5 points**: States variables can be declared **anywhere** (local/global).  
- **Partial (1-2)**: Mentions "declare at the beginning" but misses scope rules.  

#### **1.7: While vs. do...while**  
- **5 points**: "do...while executes the block **at least once**."  
- **Partial (4-4.5)**: Confuses condition evaluation order but acknowledges execution difference.  

---

### **Section 2: Classes & Constructors**  
#### **2.1: Class definition components**  
- **5 points**: Lists "data members (attributes)" and "member functions."  
- **Partial (1-2)**: Mentions "set/get functions" but omits core components.  

#### **2.2: Data member vs. local variable**  
- **5 points**: Data members are class-wide; local variables are function-specific.  
- **Partial (1-3)**: Confuses with "data vs. functioning components."  

#### **2.3: Constructor vs. function**  
- **5 points**: Constructors auto-called on object creation; no return type.  
- **Partial (2-2.5)**: Mentions initialization but conflates with general functions.  

#### **2.4: Default constructor creation**  
- **5 points**: Created by the compiler **if no user-defined constructor exists**.  

#### **2.5: Number of constructors**  
- **5 points**: "Unlimited."  
- **0 points**: Incorrect limits (e.g., "one per class").  

#### **2.6: Function prototype vs. definition**  
- **5 points**: Prototype = signature (name, return type, parameters); definition = body.  
- **Partial (4)**: Confuses parameter requirements but distinguishes declaration vs. implementation.  

#### **2.7: Header file role**  
- **5 points**: Stores class interfaces (data members, function prototypes).  
- **Partial (4-4.5)**: Mentions "hiding inner workings" but misses interface specifics.  

---

### **Section 3: Functions & Scope**  
#### **3.1: Function signature**  
- **5 points**: Includes "function name" and "parameter types."  
- **Partial (4-4.5)**: Adds unnecessary details (e.g., "description of function").  

#### **3.2: Global variable scope**  
- **5 points**: "File scope."  
- **0 points**: Incorrect scopes (e.g., "function scope").  

#### **3.3: Inline functions**  
- **5 points**: "Code is copied at each call site."  
- **Partial (4-4.5)**: Mentions "expands definition" but lacks precision.  

#### **3.4: Pass-by-reference advantage**  
- **5 points**: Avoids copying large data, improving performance.  

#### **3.5: Overloaded functions**  
- **5 points**: Differentiated by "function signature" (parameter types/order).  
- **Partial (1-3)**: Confuses with overriding/polymorphism.  

#### **3.6: Infinite recursion causes**  
- **5 points**: Incorrect recursion step or missing base case.  
- **Partial (1-3)**: Vague descriptions of recursion without specific causes.  

#### **3.7: Iteration vs. recursion similarities**  
- **5 points**: Both involve repetition, termination tests, and infinite potential.  
- **Partial (2-3.5)**: Mentions repetition but misses termination/infinite aspects.  

---

### **Section 4: Arrays & Strings**  
#### **4.1: Array length specification**  
- **5 points**: Declared size or initializer list.  
- **Partial (3-4)**: Mentions dynamic methods (e.g., `arraylist`) but omits core methods.  

#### **4.2: String vs. char[]**  
- **5 points**: Char arrays have a null terminator (`\0`); `string` is a class.  
- **Partial (3.5-4)**: Highlights safety but omits null terminator.  

#### **4.3: Passing arrays to functions**  
- **5 points**: Passed by reference.  
- **Partial (1-2.5)**: Incorrectly describes copying/returning arrays.  

#### **4.4: Static vs. non-static arrays**  
- **5 points**: Static arrays persist through program life; non-static are reinitialized.  
- **Partial (1-3)**: Confuses static with fixed-size arrays.  

#### **4.5: Multi-dimensional array dimensions**  
- **5 points**: All except the first dimension must be specified.  
- **Partial (3.5)**: Mentions indexing but misses dimension rules.  

---

### **Section 5: Sorting Algorithms**  
#### **5.1: Insertion sort idea**  
- **5 points**: Inserts elements one by one into sorted left portion.  

#### **5.2: Selection sort idea**  
- **5 points**: Repeatedly selects the minimum from the unsorted portion.  

#### **5.3: Insertion sort best-case**  
- **5 points**: O(N) operations for a pre-sorted array.  
- **Partial (2.5)**: Mentions sorted array but incorrect operation count.  

#### **5.4: Merge sort base case**  
- **5 points**: Array size ≤ 1.  
- **Partial (1-2)**: Incorrect size (e.g., 2) or unrelated answer.  

---

### **Section 6: Pointers & Memory**  
#### **6.1: Pointer definition**  
- **5 points**: "A variable containing the memory address of another variable."  
- **Partial (4-4.5)**: Mentions "accessing objects" but lacks precision.  

#### **6.2: Address (&) operator**  
- **5 points**: Returns "memory address of its operand."  
- **Partial (3.5)**: Vague terms like "returns a pointer."  

#### **6.3: Star (*) operator**  
- **5 points**: "Dereferencing operator; alias for the object pointed to."  
- **Partial (1-2)**: Incorrectly associates with characters.  

#### **6.4: Array addressing in pointer notation**  
- **5 points**: "Pointer initialized to first element, incremented with index."  
- **0 points**: Mentions "multi-dimensional array" without explanation.  

#### **6.5: sizeof operator**  
- **5 points**: Returns "size in bytes of its operand."  
- **Partial (3-4)**: Mentions "bytes" but lacks clarity.  

#### **6.6: Passing pointers to functions**  
- **5 points**: Lists four ways (e.g., constant/nonconstant pointer to data).  
- **Partial (2.5)**: Confuses with "pass by value/reference."  

#### **6.7: Function pointer**  
- **5 points**: "Address of the function code in memory."  
- **Partial (4)**: Mentions "invokes a function" but lacks technical detail.  

---

### **Section 7: Linked Lists**  
#### **7.1: Linked list definition**  
- **5 points**: "Collection of dynamically allocated nodes with links."  
- **Partial (4-4.5)**: Mentions "data structures" but omits dynamic allocation.  

#### **7.2: Linked list advantage over arrays**  
- **5 points**: "Variable length; efficient insertion/deletion."  
- **Partial (4)**: Mentions "fixed array size" but lacks specifics.  

#### **7.3: Array advantage over linked lists**  
- **5 points**: "Direct element access (random access)."  
- **Partial (4)**: Mentions "speed" but misses "random access."  

#### **7.4: Passing linked lists to functions**  
- **5 points**: "By reference."  
- **0 points**: Irrelevant answers about insertion/deletion.  

#### **7.5: Circular vs. basic linked list**  
- **5 points**: "Last node points to the head."  
- **Partial (2-3.5)**: Confuses with traversal direction (e.g., "double linked list").  

#### **7.6: Doubly-linked list advantage**  
- **5 points**: "Constant-time insertion/deletion at any position."  
- **Partial (2)**: Mentions "extra pointer" but misses efficiency.  

#### **7.7: Doubly-linked list disadvantage**  
- **5 points**: "Extra space for back pointers."  
- **0 points**: No answer.  

---

### **Section 8: Stacks & Queues**  
#### **8.1: Stack definition**  
- **5 points**: "LIFO (last-in-first-out) structure."  

#### **8.2: Stack operations**  
- **5 points**: "push and pop."  

#### **8.3: Stack implementation with array**  
- **5 points**: "Top at array end; push/pop at right side."  
- **Partial (2-3)**: Mentions "array and integer top" but lacks implementation logic.  

#### **8.4: Stack implementation with list**  
- **5 points**: "Top at list head; push/pop at beginning."  
- **Partial (2)**: Mentions "linked list" but omits pointer logic.  

#### **8.6: Infix evaluation**  
- **5 points**: "Convert to postfix, then evaluate."  

#### **8.7: Stack search operations**  
- **5 points**: "Pop elements to another stack until found, then restore."  
- **Partial (2-3)**: Mentions "push/pop" but misses storage logic.  

---

### **Section 9: Trees & Traversal**  
#### **10.1: Tree definition**  
- **5 points**: "Hierarchical nodes with root and disjoint subtrees."  
- **Partial (3-4)**: Mentions "data structure with parent/child nodes."  

#### **10.2: Tree height**  
- **5 points**: "Length of longest root-to-leaf path."  
- **Partial (4)**: Mentions "levels" but omits path length.  

#### **10.3: Leaf definition**  
- **5 points**: "Node with no children."  

#### **10.4: Binary tree definition**  
- **5 points**: "Maximum two children per node."  
- **Partial (4.5)**: Mentions "two branches" but lacks precision.  

#### **10.5: Binary search tree (BST)**  
- **5 points**: "Left child < parent < right child."  
- **Partial (2.5)**: Vague descriptions of ordering.  

#### **10.6: Inorder traversal**  
- **5 points**: "Left subtree → root → right subtree."  
- **0 points**: Incorrect traversal order (e.g., "level order").  

#### **10.7: BST search comparisons**  
- **5 points**: "Height of the tree (or log n)."  
- **0 points**: Incorrect metrics (e.g., "2-way comparison").  
