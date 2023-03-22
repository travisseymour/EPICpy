#ifndef SMART_POINTER_H
#define SMART_POINTER_H

/* Smart_Pointer class template
see R.B. Murray, C++ Strategy and Tactics. Addison-Wesley, 1993

Usage:

1. Inherit classes from Reference_Counted_Object

	class My_class : public Reference_Counted_Object {
	// rest of declaration as usual
	};

2. Always allocate objects with new and assign to a Smart_Pointer

		Smart_Pointer<const My_class> ptr = new My_class;
		or
		Smart_Pointer<const My_class> ptr(new My_class);
		
3. Can copy or assign Smart_Pointers in any way desired, e.g. with 
Standard Library containers.

4. When last Smart_Pointer pointing to an object is destructed,
or set to 0, pointed-to object will be deleted automatically.

5. Don'ts: Never delete the pointed-to object explicitly. 
Don't assign to a built-in pointer type except temporarily. 
Never assign a Smart_Pointer to point to a stack object. 
Effects of breaking these rules is undefined.
*/

/*
Reference_Counted_Objects should only be allocated using new, never the stack.
Other classes increment and decrement the use count.
If the use count hits zero as a result of decrement, the object deletes itself.
The reference count is declared mutable to allow increment/decrement_ref_count
to be declared const, so that using a Smart_Pointer on an object does not
require it to be non-const. -- check!
*/
class Reference_Counted_Object {
public:
	Reference_Counted_Object () : ref_count(0)
		{}
	Reference_Counted_Object (const Reference_Counted_Object&) : ref_count(0)
		{}
	virtual ~Reference_Counted_Object()
		{}
	void increment_ref_count() const
		{++ref_count;}
	void decrement_ref_count() const
		// suicidal - destroys this object
		{if (--ref_count == 0) delete this;}
	unsigned int get_ref_count() const
		{return ref_count;}
private:
	mutable unsigned int ref_count;	
};

/* Template for Smart_Pointer class
overloads *, ->, and =, provides conversion to built-in type.
Simply increments and decrements the reference count when Smart_Pointers
are initialized, copied, assigned, and destructed.
*/
template <class T> class Smart_Pointer {
public:
	// constructor with pointer argument - copy and increment_ref_count count
	Smart_Pointer(T* arg = 0) : ptr(arg)
		{if (ptr) ptr->increment_ref_count();}
	// templated constructor to support implicit conversions to other Smart_Pointer type
	template <class U> Smart_Pointer(const Smart_Pointer<U> other) : ptr(other.get_raw_ptr()) 
		{if (ptr) ptr->increment_ref_count();}
	// copy constructor - copy and increment_ref_count
	Smart_Pointer(const Smart_Pointer<T>& arg): ptr(arg) 
		{if (ptr) ptr->increment_ref_count();}
	// destructor - decrement ref count
	~Smart_Pointer()
		{if (ptr) ptr->decrement_ref_count();}
	// assignment - decrement lhs, increment rhs
	const Smart_Pointer<T>& operator= (const Smart_Pointer<T>& rhs)
		{
			if (ptr != rhs.ptr) {						//check for aliasing
				if (ptr) ptr->decrement_ref_count();
				ptr = rhs.ptr;
				if (ptr) ptr->increment_ref_count();
				}
			return *this;
		}
	// use these with caution - preferably only in a call, or input to Smart_Pointer ctor
	T* get_raw_ptr() const {return ptr;}	// accessor
	operator T*() const {return ptr;}   	// conversion to pointer type
	// overloaded operators
	T& operator* () {return *ptr;}
	T* operator-> () const {return ptr;}
private:
	T* ptr;
};

#endif
